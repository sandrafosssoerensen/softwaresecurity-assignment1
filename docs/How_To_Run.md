# How to run and understand the application

This guide explains how to install, start, use, test, and verify the secure
baseline of the Software Security assignment. Recorded results and unresolved
submission items are listed in [Verification](Verification.md); this guide
is not a declaration that the complete assignment is finished.

The application is a small IDS alert-analysis service with three separate
Django processes:

```text
Client → A: API/authentication → B: processing → C: storage/authorization
                                      ↓              ↓
                              alert-helper       SQLite database
```

The services communicate over HTTP. The database is storage, not one of the
three application components.

## 1. Prerequisites

The local setup uses:

- Windows PowerShell
- Python 3.12
- Git
- Internet access for installing the pinned Python dependencies

Use the directory containing `manage.py`, `Jenkinsfile`, and
`requirements.txt`. In the author's existing extraction it is
`Assignment 1/software-security-v1/software-security-v1`, not the outer
`Assignment 1` repository.

For a fresh clone (requires access to the private repository):

```powershell
git clone --branch assignment-work https://github.com/sandrafosssoerensen/softwaresecurity-assignment1.git
cd softwaresecurity-assignment1
```

For an existing checkout, open a terminal in its root instead of cloning again:

```powershell
git rev-parse --show-toplevel
git branch --show-current
git status --short --branch
```

Use the corrected `assignment-work` branch. Save/commit your own work before
switching branches. The commands below use the explicit virtual-environment
Python path, so activation is unnecessary.

## 2. Install the project

Create a virtual environment and install the application and build
dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-build.txt
```

Build and install the project-owned external package. It is installed as a
wheel and is not copied into the application source code:

```powershell
.\.venv\Scripts\python.exe -m build --wheel --no-isolation helper
.\.venv\Scripts\python.exe -m pip install --no-deps helper\dist\alert_helper-0.1.0-py3-none-any.whl
```

The package is called `alert-helper`. Component B imports it as
`alert_helper` to select and validate alert fields and to validate model
results. A and C also import the package validators through the shared views.

Check that the package is installed:

```powershell
.\.venv\Scripts\python.exe -m pip show alert-helper
```

## 3. Create local keys and test users

Run:

```powershell
.\.venv\Scripts\python.exe scripts\setup_lab.py
```

This creates local RSA keys, the authentication database, and three synthetic
lab accounts:

| User | Role | Purpose |
|---|---|---|
| `alice` | ordinary user | Own-resource tests |
| `bob` | ordinary user | Cross-user authorization tests |
| `admin` | administrator | Administrator-only actions |

The lab password is:

```text
Lab-only-Password-123!
```

These are teaching credentials only. The generated keys and runtime databases
remain under `.runtime/` and are ignored by Git. C creates its separate
analysis database when it first accesses storage. Repeating setup resets
the three lab passwords without erasing stored analyses.

A is configured with the private-key path. Local A/B/C processes still run
under the same OS user, so this is application-level separation rather than
filesystem isolation. These commands assume no previously set `DATA_DIR`,
`LAB_RUNTIME_DIR`, `B_URL`, or `C_URL` overrides.

## 4. Start the three components

Open three PowerShell terminals in the project root.

Terminal 1 — Application API A:

```powershell
.\.venv\Scripts\python.exe scripts\serve.py A
```

Terminal 2 — Processing service B:

```powershell
.\.venv\Scripts\python.exe scripts\serve.py B
```

Terminal 3 — Resource service C:

```powershell
.\.venv\Scripts\python.exe scripts\serve.py C
```

The services listen on:

| Component | Address | Responsibility |
|---|---|---|
| A | `http://127.0.0.1:8000` | Login and public API coordination |
| B | `http://127.0.0.1:8001` | Alert validation and processing |
| C | `http://127.0.0.1:8002` | Protected analysis storage and authorization |

Check that each process is running:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8001/health
Invoke-RestMethod http://127.0.0.1:8002/health
```

Only A is intended to be used by the client. B and C expose internal
endpoints used by the other services.

## 5. Use the application

### 5.1 Log in

Run all API examples in order in the same fourth terminal, from the project
root. That keeps the token and analysis variables available. Endpoint paths
have no trailing slash:

```powershell
$loginBody = @{ username = "alice"; password = "Lab-only-Password-123!" } |
    ConvertTo-Json
$login = Invoke-RestMethod `
    -Uri http://127.0.0.1:8000/auth/token `
    -Method Post `
    -ContentType "application/json" `
    -Body $loginBody
$token = $login.access_token
```

A receives the credentials and returns a short-lived RS256 JWT. The token
contains the identity, role, audience, scope, expiration, and token ID.
It expires after 900 seconds; log in again if a later request returns 401.
Do not publish live bearer tokens with your evidence.

### 5.2 Create an analysis

The example request contains a synthetic Suricata alert:

```powershell
$analysis = Invoke-RestMethod `
    -Uri http://127.0.0.1:8000/analyses `
    -Method Post `
    -Headers @{ Authorization = "Bearer $token" } `
    -ContentType "application/json" `
    -Body (Get-Content .\examples\request.json -Raw)

$analysis | ConvertTo-Json -Depth 10
$analysis.id
```

The request travels through all three components:

1. A authenticates the caller and creates scoped service tokens.
2. B verifies its token, validates the alert using `alert-helper`, and creates
   a deterministic development result.
3. C verifies the create token, binds ownership to the verified token claim,
   and stores the result.
4. The response returns C → B → A → client, with status 201.

The result identifies its model as `development-stub`; it is not a live LLM
analysis. [Design](Design.md) explains the token checks and full data flow.

### 5.3 List and read analyses

List Alice's analyses:

```powershell
Invoke-RestMethod `
    -Uri http://127.0.0.1:8000/analyses `
    -Headers @{ Authorization = "Bearer $token" }
```

Read one analysis:

```powershell
$id = $analysis.id
Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/analyses/$id" `
    -Headers @{ Authorization = "Bearer $token" }
```

Alice can read her own result, but Bob cannot read it. An administrator can
read results belonging to all users.

### 5.4 Check cross-user denial

Use the existing Alice analysis before deleting it:

```powershell
$bobLogin = Invoke-RestMethod -Uri http://127.0.0.1:8000/auth/token -Method Post -ContentType "application/json" -Body (@{ username = "bob"; password = "Lab-only-Password-123!" } | ConvertTo-Json)
try {
    Invoke-RestMethod -Uri "http://127.0.0.1:8000/analyses/$id" -Headers @{ Authorization = "Bearer $($bobLogin.access_token)" } -ErrorAction Stop
} catch {
    [int]$_.Exception.Response.StatusCode
}
```

Expected status: 404. In PowerShell, `Invoke-RestMethod` raises an error for
non-success HTTP responses; here the catch prints the denial's status.

### 5.5 Delete an analysis

Ordinary users receive `403 ADMIN_REQUIRED` when they try to delete a result.
Confirm the ordinary-user denial first:

```powershell
try {
    Invoke-RestMethod -Uri "http://127.0.0.1:8000/analyses/$id" -Method Delete -Headers @{ Authorization = "Bearer $token" } -ErrorAction Stop
} catch {
    [int]$_.Exception.Response.StatusCode
}
```

Expected status: 403. Then test the administrator control below. This deletes
only the analysis created in this walkthrough:

```powershell
$adminBody = @{ username = "admin"; password = "Lab-only-Password-123!" } |
    ConvertTo-Json
$adminLogin = Invoke-RestMethod `
    -Uri http://127.0.0.1:8000/auth/token `
    -Method Post `
    -ContentType "application/json" `
    -Body $adminBody
$adminToken = $adminLogin.access_token

Invoke-RestMethod `
    -Uri "http://127.0.0.1:8000/analyses/$id" `
    -Method Delete `
    -Headers @{ Authorization = "Bearer $adminToken" }
```

Successful deletion returns 204 with no response body. A later read of the
same ID returns 404, including for Alice.

## 6. Run the tests

The HTTP suite starts three fresh Django processes on ports 18000–18002,
creates temporary keys/databases, seeds the users, and cleans up after the run.
Keep those ports free; manually running A/B/C on 8000–8002 is not needed for
testing. The separate SQL test uses a temporary database and no HTTP servers.

Run the focused SQL-injection regression test:

```powershell
.\.venv\Scripts\python.exe tests\test_store_sql.py
```

Run the HTTP integration and authorization tests:

```powershell
.\.venv\Scripts\python.exe tests\test_flow.py
```

The secure baseline should report:

```text
Ran 1 test ... OK
Ran 9 tests ... OK
```

## 7. Vulnerability evidence

The current branch keeps size validation, owner/admin checks, parameterized
SQL, and signed ownership binding active. Existing files in
[evidence/](evidence/) have different levels of completeness:

| Experiment | Files | Interpretation |
|---|---|---|
| CWE-20 | `CWE-20-vulnerable.txt`, `CWE-20-corrected.txt` | Oversized-input acceptance and corrected rejection recorded. |
| CWE-862 | `CWE-862-vulnerable.txt`, `CWE-862-corrected.txt` | Cross-user disclosure and corrected denial recorded. |
| CWE-89 | `CWE-89-vulnerable.txt`, `CWE-89-corrected.txt` | Direct storage-level injection and parameterized correction recorded. |
| Composition/CWE-807 | `CWE-807-vulnerable.txt`, `CWE-807-corrected.txt` | Corrected test passes; vulnerable attempt fails during setup, before the intended attack. |

Use the [experiment guide](Vulnerability_Experiments_Guide.md) for reproduction,
historical CWE-862/CWE-89 snapshot issues, and the remaining composition work.
Do not enable vulnerable variants during
the normal application walkthrough.

## 8. Jenkins and CI/CD

The [Jenkinsfile](../Jenkinsfile) defines checkout, fresh Python environment,
helper build/install, Bandit, pip-audit, a high-severity Bandit gate, both test
commands, and report archiving. It currently uses Windows batch commands and
a machine-specific `PYTHON` path; adapt that path to an installed Python 3.12
accessible to the Jenkins service account on another machine.

The existing local Jenkins UI is at `http://localhost:8080/` while its
Windows service is running. This URL points to the viewer's own computer; it
is not a public evidence URL.

To review the configured job:

1. Open `software-security-assignment1-multibranch`.
2. Check that the GitHub source points to the assignment repository and uses
   a Jenkins-stored credential with the needed private-repository read access.
3. Check branch/PR discovery and the script path `Jenkinsfile`.
4. Inspect `assignment-work` builds, their revision and build cause.
5. Open Console Output and Artifacts for the selected build.

The ordinary job `software-security-assignment1-ci` produced the saved
[build #4 reports](evidence/jenkins/build-4/). They contain
`bandit.json`, `bandit.txt`, `pip-audit.json`, `test_flow.txt`, and
`test_store_sql.txt`.

Periodic multibranch scanning can discover changed branches/PRs while Jenkins
is running, but can combine multiple pushes. The `githubPush()` declaration
alone does not configure working webhook delivery. A new push build and a
PR build still need to be observed and saved to verify the assignment's
automatic-trigger requirement.

There are also open implementation issues: Windows batch blocks can mask
an earlier failed command, and no dependency approval inventory is enforced.
See [Verification](Verification.md#jenkins-evidence-and-gaps) before claiming
all release gates work. No service-log or JUnit XML artifacts are currently
produced/preserved.

## 9. Useful source files

- `app/views.py`: HTTP flow, validation, token checks, and service calls.
- `app/security.py`: JWT creation and verification.
- `app/store.py`: C's SQLite storage and ownership checks.
- `app/urls.py`: service-specific routes.
- `scripts/setup_lab.py`: local keys, database, and user seeding.
- `scripts/serve.py`: starts one component per process.
- `helper/src/alert_helper/__init__.py`: external helper package.
- `tests/test_flow.py`: HTTP and authorization tests.
- `tests/test_store_sql.py`: SQL-injection regression test.
- `docs/Design.md`: architecture, trust boundaries, and design principles.
- `docs/Verification.md`: verification results and limitations.

## 10. Stop and troubleshoot

Stop each manually started service with Ctrl+C in its terminal.
Runtime analyses remain on disk for the next run.

| Symptom | Check |
|---|---|
| Python or `.venv` path not found | Use the repository root and complete installation with Python 3.12. |
| `No module named alert_helper` | Build/install the helper with the same `.venv` Python used to run the app. |
| Missing key file or failed seeded login | Run `scripts/setup_lab.py` in the intended local environment. |
| Address already in use | Stop the earlier service you started, or free ports 8000–8002 / test ports 18000–18002. |
| 401 | Log in again; check the Bearer header and that the client uses A. |
| 403 on delete / 404 for Bob's read | Expected authorization denial for these examples. |
| 400 | Check exact JSON fields and endpoint path; avoid adding an owner field. |
| 503/504 | Check B/C health and their terminal output. |
| Browser shows 404 at `/` | This is an API without a homepage; use `/health` or the documented API requests. |
| Git shows unexpected branches | Check `git rev-parse --show-toplevel`; the outer extraction may be another repository. |

For evidence, save each run under a new filename and record the commit/command.
Do not overwrite historical vulnerable/corrected logs to make them look like
new runs.

## 11. Known limitations

The current processing result uses a deterministic development model stub. It
does not prove real model accuracy or production readiness. Docker Compose has
not been verified in the local run. Protected transport, key rotation,
durable background processing, monitoring, and production model evaluation
remain unimplemented production considerations. The assignment does not require
Ollama or Docker specifically. Remaining required work is listed separately in
[Verification](Verification.md#remaining-work-before-claiming-submission-completion).
