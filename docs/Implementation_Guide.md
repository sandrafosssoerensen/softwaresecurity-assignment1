# Software Security Assignment: From-Empty-Repository Implementation Guide

This guide assumes that the repository contains no implementation yet. It explains what to create, in what order to create it, what material to add, and what evidence to collect for the assignment.

The goal is not only to make the application work. You should be able to explain every component, security decision, vulnerability experiment, test, and report claim yourself.

## 1. Assignment requirements

The final submission must contain:

- a small useful application;
- three separate application components running as separate processes;
- communication through an explicit interface such as HTTP;
- authentication and authorization;
- at least two ordinary users and one privileged user;
- at least three functionalities;
- at least one functionality involving all three components;
- one separately installed helper package;
- three intentionally planted catalogue vulnerabilities;
- one additional vulnerability caused by composing the components;
- an initial SSDLC plan committed before feature implementation;
- a Jenkins pipeline for build, analysis, testing, and artifacts;
- a report of approximately 2,000–2,500 words;
- an AI-use declaration;
- a README with exact setup and execution commands;
- the complete Git history.

The malicious supply-chain package exercise is optional. The benign helper package is required.

## 2. Choose and describe the application first

Use one small domain with synthetic data. The existing design idea is an IDS alert-analysis application:

```text
Client submits a Suricata alert
        ↓
Application analyses it
        ↓
User retrieves a protected analysis result
```

Define these items in a short requirements document before coding:

### Users

- `alice` — ordinary user
- `bob` — ordinary user
- `admin` — privileged user

### Protected resource

An analysis result belongs to exactly one user.

### Functionalities

At least these four can be implemented:

1. Authenticate a user.
2. Create an analysis.
3. List and read analyses.
4. Delete an analysis as an administrator.

### Security rules

- Ordinary users may create analyses.
- Ordinary users may list and read only their own analyses.
- Administrators may list and read all analyses.
- Only administrators may delete analyses.
- The processing service may create only the specific result assigned to it.
- The processing service may not delete or freely read stored results.

## 3. Create the repository structure

Start with a structure similar to this:

```text
software-security-v1/
├── app/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── views.py
│   ├── security.py
│   └── store.py
├── helper/
│   ├── pyproject.toml
│   └── src/alert_helper/__init__.py
├── examples/request.json
├── scripts/setup_lab.py
├── scripts/serve.py
├── tests/test_flow.py
├── docs/
│   ├── SSDLC_Plan.md
│   ├── Design.md
│   ├── Verification.md
│   ├── AI_Use.md
│   └── Implementation_Guide.md
├── manage.py
├── requirements.txt
├── requirements-build.txt
├── Dockerfile
├── compose.yaml
├── Jenkinsfile
└── README.md
```

Add the assignment PDF, initial design material, diagrams, logs, and other permitted supporting material in an appropriate `docs/` or `artifacts/` directory. Do not commit passwords, private keys, virtual environments, or runtime databases.

## 4. Write the initial SSDLC plan before implementation

Create `docs/SSDLC_Plan.md` and commit it before writing application features.

The plan should contain four phases:

| Phase | Deliverable | Gate |
|---|---|---|
| Requirements | Scope, operations, assets, trust boundaries, access matrix, STRIDE analysis | Architecture and permissions reviewed |
| Implementation/build | Three components, helper dependency, reproducible setup | Build succeeds and dependencies are approved |
| Testing | Functional tests, authorization tests, vulnerability experiments | Required tests pass and attacks are corrected |
| Release/operation | Production limitations and operational requirements | Report documents remaining risks |

Use this traceability format:

```text
Asset → threat → control → lifecycle activity → test/evidence → gate decision
```

Include at least these threats:

- oversized input and denial of service;
- missing authorization and information disclosure;
- SQL injection and query integrity;
- incorrect trust between components;
- forged or misused tokens.

Commit this plan before implementation. Do not delete the commit later.

## 5. Set up Python and dependencies

Use Python 3.12 and create a virtual environment:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-build.txt
```

Pin the dependencies. The project should not silently download unapproved or unrecorded packages.

Build the helper package as an installable wheel:

```powershell
.\.venv\Scripts\python.exe -m build --wheel --no-isolation helper
.\.venv\Scripts\python.exe -m pip install --no-deps helper\dist\alert_helper-0.1.0-py3-none-any.whl
```

The helper must be imported as an installed dependency. Do not copy its source code into `app/`.

## 6. Implement the three components in dependency order

Implement and understand one layer at a time. After each layer, run a small test before continuing.

### Step 1: Create `manage.py`

`manage.py` is the command-line entry point for Django. It should set:

```python
DJANGO_SETTINGS_MODULE = "app.settings"
```

It should support commands such as:

```powershell
python manage.py runserver
python manage.py migrate
```

### Step 2: Create `app/settings.py`

Configure Django, the URL configuration, allowed hosts, database locations, service name, input-size limit, and secret/key paths.

Use an environment variable to select the service:

```python
SERVICE = os.environ.get("SERVICE", "A")
```

The three processes may use the same code but different settings values.

### Step 3: Create `app/urls.py`

Route endpoints according to the service:

```text
A:
  /health
  /auth/token
  /analyses
  /analyses/{id}

B:
  /health
  /internal/analyze

C:
  /health
  /internal/analyses
  /internal/analyses/{id}
```

The routes should expose different responsibilities for A, B, and C.

### Step 4: Implement authentication in A

Seed two ordinary users and one administrator. Implement a login endpoint that accepts credentials, authenticates against Django, rejects invalid credentials, and issues a short-lived access token.

The token must identify:

- the user;
- the target service;
- the permitted action;
- the role;
- the expiration time;
- the token ID.

### Step 5: Implement `app/security.py`

Use a standard JWT library with RS256.

A should own the private key. B and C should only receive the public key.

Verification must check the signature, algorithm, issuer, audience, expiration, required claims, operation scope, role, and analysis ID where relevant.

Do not invent a cryptographic algorithm.

### Step 6: Implement the helper package

The helper should validate and select the required alert fields:

- event type;
- timezone-aware timestamp;
- source and destination IP addresses;
- protocol;
- positive signature ID;
- nonblank signature;
- severity between 1 and 3;
- optional ports between 0 and 65535.

It should also validate the analysis result structure.

Build it as a wheel and install it before running the application.

### Step 7: Implement B

B should verify its execution token, validate the request body, enforce the 64 KiB compact UTF-8 JSON limit, use the installed helper package, process only selected alert fields, produce an analysis result, validate that result, and submit it to C with a limited create token.

The development version can use a deterministic stub while testing. If Ollama is required for the final system, integrate it after the secure baseline works.

### Step 8: Implement C storage

Create a separate SQLite database owned by C.

The storage table should include the analysis ID, verified owner, original alert, selected input, model information, prompt metadata, settings, timestamp, latency, and result.

Use parameterized SQL queries:

```python
db.execute(
    "SELECT * FROM analyses WHERE id=?",
    (analysis_id,)
)
```

C must perform authorization checks for every operation, including requests arriving from another service.

## 7. Test the secure baseline

Write tests before starting the vulnerability experiments.

### Functional tests

- login succeeds for seeded users;
- invalid login fails;
- analysis creation succeeds;
- analysis is saved;
- analysis can be read;
- analysis can be listed;
- admin can delete an analysis.

### Authorization tests

- Alice can access her own analysis;
- Alice cannot access Bob's analysis;
- Bob cannot access Alice's analysis;
- ordinary users cannot delete;
- admin can access all analyses;
- B's create token cannot delete;
- expired tokens fail;
- forged tokens fail;
- wrong-audience tokens fail.

### Input tests

- malformed JSON fails;
- unexpected fields fail;
- missing fields fail;
- malformed alerts fail;
- oversized alerts fail;
- malformed model results fail.

Run tests from the project root using the virtual environment:

```powershell
.\.venv\Scripts\python.exe tests\test_flow.py
```

## 8. Implement the four vulnerability experiments

The final secure application should not retain vulnerable code. Use separate branches or commits for the experiments.

For every vulnerability:

1. Start from the secure baseline.
2. Remove or weaken one control.
3. Run a controlled test.
4. Save the output and logs.
5. Restore the control.
6. Run the same test again.
7. Record the corrected result.

### CWE-20: missing input-size validation

Temporarily remove B's 64 KiB check. Send an oversized request and record that it reaches processing. Restore the check and record the `413 INPUT_TOO_LARGE` response.

### CWE-862: missing authorization

Temporarily remove C's ownership check. Let Alice create a result and have Bob request it. Record the vulnerable disclosure. Restore the owner/admin check and record the denial.

### CWE-89: SQL injection

Temporarily construct a query unsafely using user input. Use a controlled test input and document the actual effect. Restore parameterized SQL and repeat the test.

### Composition vulnerability

Temporarily make C trust an owner field supplied by B instead of using verified token claims. Demonstrate the incorrect ownership behavior. Restore the signed owner and analysis-ID binding and retest.

For each experiment, document the vulnerable code or changed control, reachability conditions, test request, observed effect, affected security property, correction, corrected test result, relevant Git commit, and log file.

## 9. Add the Jenkins pipeline

Create `Jenkinsfile` after the local setup is reproducible.

The pipeline must run on pushes and pull requests and should:

1. install approved dependencies;
2. build or validate all components;
3. build the helper wheel;
4. run static analysis such as Bandit;
5. run dependency analysis such as pip-audit;
6. start a fresh test environment;
7. seed fresh users and databases;
8. run functional and authorization tests;
9. save test, scan, and service logs as artifacts;
10. fail when required security or quality gates fail.

Document which findings block a release. Required security failures, unresolved high-severity findings, and unapproved dependencies should block release.

## 10. Produce the documentation and artifacts

### `README.md`

Include the application purpose, architecture summary, dependency installation, helper build command, database setup and seeding, commands to start A/B/C, test command, example API requests, and known limitations.

### `docs/Design.md`

Include component responsibilities, data flow, trust boundaries, access-control matrix, assets, STRIDE analysis, and secure design principles.

### `docs/Verification.md`

Record the test environment, commands executed, test results, vulnerability experiment results, corrections, and remaining limitations.

### `docs/AI_Use.md`

Accurately describe what AI helped produce, what you reviewed, what you changed, which tests you ran, which experiments you performed, and what was not generated or verified by AI.

### Final report

Organize the report around:

1. System purpose and domain choice.
2. Architecture and component boundaries.
3. Identity, authority, ownership, and dependency trust.
4. Data flow and authorization sequence.
5. Three secure design principles.
6. SSDLC and Jenkins gates.
7. Four vulnerability experiments.
8. Corrections and retesting.
9. Production requirements and limitations.

Support claims with commits, code references, tests, logs, and Jenkins artifacts.

## 11. Suggested Git milestones

Use small commits that reflect the lifecycle:

```text
requirements: define scope and security requirements
ssdlc: commit initial four-phase plan
architecture: add component and data-flow design
setup: add Django project and dependencies
helper: add and install helper package
auth: implement users, roles, and JWTs
components: implement A, B, and C
tests: add secure functional and authorization tests
experiment: CWE-20 vulnerable version
fix: restore CWE-20 protection
experiment: CWE-862 vulnerable version
fix: restore ownership authorization
experiment: CWE-89 vulnerable version
fix: restore parameterized SQL
experiment: composition vulnerability
fix: restore signed ownership binding
model: implement or integrate final model behavior
ci: add Jenkins pipeline
docs: complete verification, report, and AI declaration
```

Keep the vulnerable experiments isolated and make the final branch secure.

## 12. How to work so you understand the code

For each file:

1. Read it without copying it.
2. Explain each function in your own words.
3. Identify trusted and untrusted inputs.
4. Write a small test for the expected behavior.
5. Implement or reproduce one function.
6. Run the test.
7. Commit the working change.

For each request, draw this sequence:

```text
Client → URL route → view → validation → authorization → database/service → response
```

For each security control, ask:

- What threat does it address?
- Which component enforces it?
- Can another component bypass it?
- What test proves that it works?

## 13. Final completion checklist

- [ ] Initial SSDLC plan was committed before feature implementation.
- [ ] Application has three separate running components.
- [ ] Components communicate through HTTP or another explicit interface.
- [ ] Helper package is installed as a dependency.
- [ ] Authentication works.
- [ ] Two ordinary users and one admin are seeded.
- [ ] At least three functionalities work.
- [ ] One functionality uses all three components.
- [ ] Resource ownership is enforced by C.
- [ ] At least three secure design principles are explained and tested.
- [ ] CWE-20 was demonstrated and corrected.
- [ ] CWE-862 was demonstrated and corrected.
- [ ] CWE-89 was demonstrated and corrected.
- [ ] Composition vulnerability was demonstrated and corrected.
- [ ] Functional and authorization tests pass.
- [ ] Jenkins builds, scans, tests, and archives artifacts.
- [ ] README contains exact commands.
- [ ] Report is complete and evidence-based.
- [ ] AI-use declaration is complete.
- [ ] Full Git history is preserved.

## Recommended order

```text
Requirements and initial SSDLC plan
→ project setup
→ helper package
→ authentication
→ A, B, and C components
→ secure baseline tests
→ vulnerability experiments
→ corrections and retesting
→ model integration
→ Jenkins
→ report and final artifacts
```
