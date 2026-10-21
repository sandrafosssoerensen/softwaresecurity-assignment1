# How to run and understand the application

This guide shows how to install and use the corrected application, run its
tests, compare versions, and access Jenkins. It also includes an optional
ZAP scan. [Verification](Verification.md) records test results and evidence
limitations. [Terminology](Terminology.md) explains technical words used here.

The application processes test alerts from an intrusion detection system
(IDS). Three Django services run as separate programs:

```text
Client → component A: login and requests → component B: processing → component C: storage and access checks
                                      ↓              ↓
                              alert-helper       SQLite database
```

The services send HTTP requests to each other. The database stores records.
it does not count as one of the three application services.

## 1. Prerequisites

The local setup uses:

- Windows PowerShell
- Python 3.12
- Git
- Internet access to download the Python packages listed in the requirements

Use the directory containing `manage.py`, `Jenkinsfile`, and
`requirements.txt`. In the author's existing extraction it is
`Assignment 1/software-security-v1/software-security-v1`, not the outer
`Assignment 1` repository.

For a fresh clone (requires access to the private repository):

```powershell
git clone --branch main https://github.com/sandrafosssoerensen/softwaresecurity-assignment1.git
cd softwaresecurity-assignment1
```

For an existing checkout, open a terminal in its root instead of cloning again:

```powershell
git rev-parse --show-toplevel
git branch --show-current
git status --short --branch
```

Use the corrected `assignment-work` branch. Save/commit your own work before
switching branches. Each command below names the Python executable inside the virtual environment
(a separate package environment for this project), so you do not need to
activate it first.

## 2. Install the project

Create a virtual environment and install the application and build
dependencies. If the Windows `py` launcher is unavailable, first confirm
`python --version` is 3.12 and use `python -m venv .venv` instead:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-build.txt
```

Build and install your own helper package. A wheel is an installable Python
package file ending in `.whl`. This keeps the helper as an installed package:

```powershell
.\.venv\Scripts\python.exe -m build --wheel --no-isolation helper
.\.venv\Scripts\python.exe -m pip install --no-deps helper\dist\alert_helper-0.1.0-py3-none-any.whl
```

The package name is `alert-helper`. Python code imports it as `alert_helper`.
Component B uses its functions to select alert fields and check the alert and result.
Component A and component C also use these checks through the shared request-handling code.

Check that the package is installed:

```powershell
.\.venv\Scripts\python.exe -m pip show alert-helper
```

## 3. Create local keys and test users

Run:

```powershell
.\.venv\Scripts\python.exe scripts\setup_lab.py
```

This creates the keys used to sign/check tokens, component A's user database, and
three test accounts:

| User | Role | Purpose |
|---|---|---|
| `alice` | ordinary user | Creates and reads her own analyses. |
| `bob` | ordinary user | Checks that a second user cannot read Alice's analyses. |
| `admin` | administrator | Reads all analyses and can delete them. |

The lab password is:

```text
Lab-only-Password-123!
```

These are teaching credentials only. The generated keys and runtime databases
remain under `.runtime/` and are ignored by Git. Component C creates its separate
analysis database when it first accesses storage. Repeating setup resets
the three lab passwords without erasing stored analyses.

Only component A is given the private-key path in its normal launch settings. However,
all three programs run under the same Windows account, which may let them
read the same files. They have different application permissions, but their
file access is not isolated by Windows. These examples assume you have not
set custom `DATA_DIR`, `LAB_RUNTIME_DIR`, `B_URL`, or `C_URL` values.

## 4. Start the three components

Open three PowerShell terminals in the project root.

Terminal 1 — Component A — application API:

```powershell
.\.venv\Scripts\python.exe scripts\serve.py A
```

Terminal 2 — Component B — processing service:

```powershell
.\.venv\Scripts\python.exe scripts\serve.py B
```

Terminal 3 — Component C — resource service:

```powershell
.\.venv\Scripts\python.exe scripts\serve.py C
```

The services listen on:

| Component | Address | Responsibility |
|---|---|---|
| Component A | `http://127.0.0.1:8000` | Checks logins and sends user requests to component B and component C. |
| Component B | `http://127.0.0.1:8001` | Checks alerts and produces results. |
| Component C | `http://127.0.0.1:8002` | Stores results and checks who may access them. |

Check that each process is running:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8001/health
Invoke-RestMethod http://127.0.0.1:8002/health
```

Send user requests to component A. Component B and component C have routes intended for requests from other
services. The word `internal` in those routes does not itself protect them.
They are protected by token and permission checks.

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

Component A checks the username/password and returns a signed login token (JWT).
The token contains the user ID, role, intended service, allowed action,
expiry time, and a token ID. It is signed using the existing RS256 algorithm.
It expires after 900 seconds. Log in again if it expires. Do not include
live tokens in published reports. [Design](Design.md#authentication-and-authority-binding)
explains the token fields.

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

1. Component A checks the user's token and creates two tokens: one permitting component B to
   process the alert and one permitting component C to store that analysis for the user.
2. Component B checks the tokens and alert using `alert-helper`, then produces a simple
   development result.
3. Component B sends the result to component C together with component A's existing storage token.
4. Component C checks that token and stores the owner from its signed user ID.
5. The result returns component C → component B → component A → client with status 201 (created).

The model is labelled `development-stub`: a fixed-format summary used in
place of a real AI model. [Design](Design.md) explains the full data flow.

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
non-success HTTP responses. Here the catch prints the denial's status.

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

The HTTP tests start three new Django processes, create temporary
keys/databases and known users, and clean up afterwards. Each process
binds its own unused loopback port allocated by the operating system.
The processes report their addresses before requests begin, so separate
branch jobs do not share test listeners. Manually running component A,
component B, and component C on 8000–8002 is not needed for testing.
The SQL test uses a temporary database and no HTTP servers.

Run the dependency-gate tests as well:

```powershell
.\.venv\Scripts\python.exe tests\test_dependency_gate.py
```

Run the SQL test, which checks that the injection bug remains fixed:

```powershell
.\.venv\Scripts\python.exe tests\test_store_sql.py
```

Run the HTTP tests, which check the services working together and their permission rules:

```powershell
.\.venv\Scripts\python.exe tests\test_flow.py
```

The corrected version should report:

```text
Ran 6 tests ... OK
Ran 1 test ... OK
Ran 10 tests ... OK
```

### 6.1 Compare the vulnerable and fixed branches

The repository contains separate comparison branches. Save or commit local
changes and stop manually started services before switching code. Install
Bandit once in the local venv if it is not already present:

```powershell
.\.venv\Scripts\python.exe -m pip install bandit==1.9.4
```

The commands below run the same tests and scan the same source folder as
Jenkins. This repository has no `run.bat --scan` command. Run commands one
after the other, save your changes before switching, and record the commit
shown by `git rev-parse HEAD`.

Run the version with the four deliberately enabled flaws:

```powershell
git switch vulnerable-version
git rev-parse HEAD
.\.venv\Scripts\python.exe tests\test_store_sql.py
.\.venv\Scripts\python.exe tests\test_flow.py
.\.venv\Scripts\python.exe -m bandit -r app -f screen --exit-zero
```

This branch is expected to fail security tests. The failures demonstrate the
four planted vulnerabilities and must not be presented as a secure release.
The HTTP suite has four expected failures, including the SQL-injection request
sent through the public API. The direct SQL test also fails because the unsafe
query returns Alice's record for the injected ID.

Run the corrected version:

```powershell
git switch fixed-version
git rev-parse HEAD
.\.venv\Scripts\python.exe tests\test_store_sql.py
.\.venv\Scripts\python.exe tests\test_flow.py
.\.venv\Scripts\python.exe -m bandit -r app -f screen --exit-zero
```

This branch is expected to report one direct SQL test and ten HTTP tests
passing. The HTTP SQL-injection request receives 400 before it reaches the
query. B608 should be absent.
The final working branch is `assignment-work`. Switch back to it after the
comparison:

```powershell
git switch assignment-work
```

The expected Jenkins result is red for `vulnerable-version` and green for
the corrected versions. The saved comparison shows the intended failures.
The updated Jenkinsfile checks each suite's exit code, including the SQL
suite even if the later HTTP suite passes. Current Jenkins builds show green
corrected versions and a blocked combined vulnerable version. A separate
SQL-only Jenkins experiment is optional.
See [Verification](Verification.md#failure-propagation).
`--exit-zero` saves/displays findings without making the scan command fail.

## 7. Vulnerability evidence

Use the [Jenkins comparison index](evidence/jenkins/README.md) for the saved
builds and the [isolated composition results](evidence/composition-isolated/README.md)
for the additional local experiment:

| Control | Vulnerable result | Fixed result |
|---|---|---|
| CWE-20 input size | Oversized alert accepted with 201. | Size test passes, expecting 413. |
| CWE-862 ownership | Bob reads Alice's result with 200. | Bob receives 404. Owner/admin controls pass. |
| CWE-89 SQL | The HTTP injection request returns Alice's selected record, and the direct SQL test also returns a record. | The HTTP route rejects the malformed ID with 400, and the direct SQL test treats the payload as data. |
| Composition/CWE-807 | Token permitting creation for Alice is used to store owner 2 (Bob). Bob reads with 200. | Request owner field is rejected with 400. Later read is 404. |

The current fixed Jenkins run passes ten HTTP tests and one direct SQL test.
The current vulnerable Jenkins run has four HTTP failures and one SQL failure.
Bandit detects the unsafe SQL construction (B608). Both scans also warn about `Bearer`
(B105). That warning is a false positive: the word names the token scheme,
not a secret password.

Older per-CWE files remain as history, including the unsuccessful initial
composition attempt. The newer vulnerable version can be run. See the
[experiment guide](Vulnerability_Experiments_Guide.md) for the setup,
code fixes, and limits on what each result proves when several flaws are
active together.

For the supplementary composition-only comparison, use
`experiment-composition-isolated` and `fixed-version`. On each branch run:

```powershell
.\.venv\Scripts\python.exe tests\test_composition_isolated.py
```

The experimental version should fail with `201 != 400`, after confirming that
Bob cannot read Alice's ordinary analysis. The fixed version should pass.
The [isolated experiment guide](Composition_Isolation.md) contains the full
branch-switching commands, observations, and source references. Return to
`assignment-work` after the comparison.

## 8. Jenkins and CI/CD

The [Jenkinsfile](../Jenkinsfile) defines the automated steps: download the
branch, create a Python environment, build/install the helper, check source
and packages, run tests, and save reports. Bandit checks source code.
pip-audit checks package versions against known vulnerability reports.
A gate is a rule deciding whether a failure must stop the build.

### 8.1 Prepare a Windows Jenkins agent

The Jenkins agent is the computer/process that runs the build commands.
It needs Git, Python 3.12, and network access to the private repository and
package download/advisory services. Python must be accessible to the account
running Jenkins. PATH is the list
of folders Windows searches for commands. Creating a separate variable
called `python312` does not add that folder to PATH.

The Build stage runs `where python` and `python --version`. If those fail,
correct the service account/system PATH, restart the Jenkins service through
an administrator terminal, and rerun the build. Keep personal installation
paths in the agent's configuration rather than hardcoding them in source.

```powershell
Restart-Service jenkins
```

The working and comparison branches now use the same portable Jenkinsfile
and test harness. Their application protections still differ as intended.

### 8.2 Configure and access the multibranch job

Open `http://localhost:8080/` while your Jenkins service is running. This
address refers to the viewer's own machine. Log in with the Jenkins account
created during setup. `initialAdminPassword` is for the first setup unlock.
it is not the ordinary password after creating the admin account.

For a fresh Jenkins installation, install Pipeline, Git, and GitHub Branch
Source support and create a **Multibranch Pipeline** job:

1. Add a GitHub source for
   `https://github.com/sandrafosssoerensen/softwaresecurity-assignment1`.
2. Select a Jenkins-stored credential with repository read access. For a
   fine-grained token, select this private repository and grant the relevant
   contents/metadata and pull-request read permissions. Grant commit-status
   write only if Jenkins posts statuses.
3. Enable branch discovery and origin pull-request discovery, use
   `Jenkinsfile` as script path, save, and scan the repository.
4. Check that `assignment-work`, `fixed-version`, and
   `vulnerable-version` are discovered when their remote heads contain a
   Jenkinsfile. A branch with no Jenkinsfile is skipped.
5. Open a branch build's Console Output and Artifacts (saved files). Check
   the commit, why the build started, each stage's result, and the test reports.

The existing job is named `software-security-assignment1-multibranch`.
Job configuration and stored credentials are external to the repository.
a clone alone does not create them.

### 8.3 Automatic triggers, gates, and archived output

The current job periodically checks the repository for changes. Push delivery
appeared in the assignment-work #9 console, and current corrected and
vulnerable branch builds have run with the updated pipeline. The Jenkins
evidence index distinguishes automatic, periodic, and manual build causes.

A webhook is a notification GitHub sends to Jenkins after an event such as
a push. GitHub must be able to reach Jenkins' `/github-webhook/` route.
A GitHub-hosted webhook cannot deliver directly
to your computer's `localhost`. Record the reachable delivery setup and
successful delivery/build cause used in the demonstration. Keep credentials
and webhook secrets outside the source/evidence.

The pipeline saves `dependency-approval.json`, `bandit.json`, `bandit.txt`,
`pip-audit.json`, `test_dependency_gate.txt`, `test_store_sql.txt`, and
`test_flow.txt` when those steps produce them. Tests use text reports rather
than JUnit XML. Earlier archives contain only the reports produced then.

The Bandit gate stops only on high-severity findings, so low B105 and medium
B608 do not stop that stage. The SQL test checks the actual unsafe query
behavior. Package audit findings, unapproved package names or versions,
build errors, and any required test failure stop the updated pipeline.
The approval stage compares the installed inventory against all three
requirements files and `ci/approved-local.txt`. To reproduce that stage,
use a fresh environment and include `-r requirements-ci.txt` when installing
requirements. Your ordinary development environment may contain extra tools
that correctly fail the approval check.
See [Verification](Verification.md#jenkins-evidence).

HTTP suites can run concurrently because they allocate separate test ports.
`disableConcurrentBuilds()` additionally prevents overlap within one branch job.

### 8.4 Optional OWASP ZAP assessment

OWASP ZAP checks a running web service for possible security problems.
It is outside the demonstrated verification scope and does not replace the
functional or permission tests. An optional assessment uses the local test
environment and targets component A at:

```text
http://127.0.0.1:8000
```

Use ZAP's automated scan workflow if available in your installed edition, or
provide the authenticated JSON requests from the API walkthrough. A scan of
only the root URL checks very little: this API has no homepage, and protected
routes require tokens. Record which routes were checked and how requests were
authenticated. A scan with no findings does not prove that all permission
checks work.

An active scan can create or modify test data. Stop services before changing
comparison branches and restart them from the intended version. Save a
generated report under a labelled directory such as `docs/evidence/zap/`,
with revision, target, date, and scope. Review the export for live tokens,
private keys, or credentials before committing it. ZAP is optional. No
`run.bat` or port-5000 service is needed for this application.

## 9. Useful source files

- `app/views.py`: HTTP flow, validation, token checks, and service calls.
- `app/security.py`: JWT creation and verification.
- `app/store.py`: component C's SQLite storage and ownership checks.
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
| Python or `.venv` path not found | Use the repository root and complete installation with Python 3.12. For Jenkins, check its service PATH and Build-stage executable/version output. |
| `No module named alert_helper` | Build/install the helper with the same `.venv` Python used to run the app. |
| Missing key file or failed seeded login | Run `scripts/setup_lab.py` in the intended local environment. |
| Address already in use | Stop the earlier manual service you started, or free its port in 8000–8002. Tests allocate their own ports. |
| 401 | Log in again. Check the Bearer header and that the client uses component A. In CI, check startup logs and confirm all services use that run's temporary keys. |
| 403 on delete / 404 for Bob's read | Expected authorization denial for these examples. |
| 400 | Check exact JSON fields and endpoint path. Avoid adding an owner field. |
| 503/504 | Check component B and component C health and their terminal output. |
| Browser shows 404 at `/` | This is an API without a homepage. Use `/health` or the documented API requests. |
| Git shows unexpected branches | Check `git rev-parse --show-toplevel`. The outer extraction may be another repository. |

Save new results separately, with the command and commit, so they are easy
to compare with earlier runs.

## 11. Known limitations

The current processor builds a fixed development summary instead of using
a real model. It is not intended or evaluated as a real threat-assessment
model.
The optional Docker Compose setup has passed a local build, three-component
health check, and authenticated create/read/delete smoke test on Rancher
Desktop. This does not establish production-grade container isolation.
Encrypted transport, key replacement, reliable background processing,
monitoring, and model assessment are future production needs. The assignment
does not require Ollama or Docker specifically. The sanitized output is in
[Docker evidence](evidence/docker/README.md). Test and CI limitations are
described in [Verification](Verification.md).
