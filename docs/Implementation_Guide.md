# Learning guide: rebuild the application from an empty repository

Use this guide to practise rebuilding the application in a separate folder.
It explains what to implement first and how the pieces fit together.

To run the existing project, use [How to run](How_To_Run.md).
For unfinished work, see [Verification](Verification.md).
[Terminology](Terminology.md) explains technical words.

## 1. Understand the scope before coding

The assignment requires three separate programs that communicate,
login and permission checks, at least three functions, two ordinary users,
one administrator, and your own helper installed as a package. At least
one function must use all three programs.

It also requires three catalogue flaws, one additional flaw caused by how
the services work together, a four-phase security plan committed before code,
Jenkins checks on pushes/pull requests, saved results, a report, an AI-use
declaration, and full Git history.

The chosen workflow is:

```text
Submit alert → check and summarise → store result → read permitted result
```

The processor uses a fixed development summary. A real AI model, website
pages, Docker, and the optional malicious-package experiment are not required.
The ordinary installable helper is required.

Read [Design](Design.md) and explain:

- Why Alice can read her own result but Bob cannot.
- Why admin can read all results and delete them.
- Why component B gets permission for only one processing/storage task.
- Why component C checks requests even when they come from another service.
- Why a database or imported package does not count as a separate program.

## 2. Write the plan and design

For a new learning project, commit the plan before implementing features.
The existing assignment already has its original plan in `8e1b610`.

Describe what the application must do, what data needs protection, how data
moves, who may do what, possible attacks, and the controls. Follow:

```text
What needs protection → possible threat → protection → development activity
→ test or evidence → decision about continuing/releasing
```

The phases are requirements, implementation/build, testing, and
release/operation. [SSDLC_Plan.md](SSDLC_Plan.md) explains them and
distinguishes planned protections from checks that actually run.

## 3. Create the project structure

Use the existing files as references:

```text
app/                 Django settings, routes, request handlers, tokens, storage
helper/              Separate installable package
scripts/             setup_lab.py and serve.py
examples/            request.json
tests/               test_flow.py and test_store_sql.py
docs/                Explanations, guides, and saved evidence
manage.py            Starts Django commands
requirements.txt     Application package versions
requirements-build.txt
Jenkinsfile          Automated build/check steps
README.md
```

Keep generated keys, databases, virtual environments, and real credentials
outside Git. The documented password is for synthetic lab accounts only.

## 4. Install dependencies and the helper

After creating the requirements and helper files:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-build.txt
.\.venv\Scripts\python.exe -m build --wheel --no-isolation helper
.\.venv\Scripts\python.exe -m pip install --no-deps helper\dist\alert_helper-0.1.0-py3-none-any.whl
```

The package name in `helper/pyproject.toml` is `alert-helper`. The
Python import name is `alert_helper`. A wheel is its installable file.

`select_alert()` checks input and selects the fields used for processing.
`validate_result()` checks the output fields. Component B imports these installed
functions. It does not keep a copied package inside `app/`.

An exact version such as `Django==5.2.18` is pinned. Pinning helps repeated
setup. The pipeline also checks every installed package against exact
approved names and versions. Read `requirements-ci.txt`,
`ci/approved-local.txt`, and `scripts/check_dependencies.py` for that gate.
Pinning and inventory checks do not verify a package's file contents.

## 5. Implement one layer at a time

### Django entry points and routing

Read `manage.py`, `app/settings.py`, `app/urls.py`, and
`scripts/serve.py`.

The `SERVICE` value selects component A, component B, or component C. Each runs the same source files
in a separate process, with its own routes and data settings. Only component A loads
Django's user-account database.

Explain why running three processes differs from defining three classes
inside one process.

### Users and signed authority

Read `scripts/setup_lab.py`, `login()`, and `app/security.py`.

Setup creates RSA keys, prepares component A's database, and creates alice/bob/admin.
Django checks passwords. Component A treats the admin account's `is_staff` flag as
the administrator role.

Component A signs tokens containing the user and permitted action. Services check
the signature, issuer, intended service, expiration, required fields,
action, and role. The views also check analysis IDs.

Use the [token table](Design.md#authentication-and-authority-binding) to
explain which service receives each token. Component B passes component A's storage token to component C.
it does not sign a new one.

Only component A is configured with the private-key path, but all local processes
share the same Windows account. This setup does not isolate their files.

### Component C — resource service

Read `app/store.py` and `stored_analyses()`.

Component C stores an ID, owner, and JSON document for each analysis. SQL parameters
keep supplied values separate from query syntax:

```python
db.execute("SELECT * FROM analyses WHERE id=?", (analysis_id,))
```

Component C's HTTP handler checks the token and requested action/analysis ID.
The store checks ownership on read and filters lists. The handler checks
admin before calling `store.delete()`.

Explain why a hard-to-guess ID is not a replacement for permission checks.

### Component B — processing service

Read `analyze()`.

Component B checks permission to process, checks input size, validates alert fields,
and checks that the token permitting storage in component C names the same user and
analysis. It creates the development result and sends it to component C together
with that existing token. Component C checks the request independently.

Explain why component C should trust the signed user ID rather than an `owner_id`
chosen in the request body.

### Component A — public API and service calls

Read `public_analyses()`, `body()`, `authority()`, `relay()`,
and `endpoint()`.

Component A checks the user's token, chooses an analysis ID, and asks component B to process
using limited tokens. List/read/delete requests go from component A directly to component C.
The response travels back through component A. The endpoint wrapper converts known
errors into HTTP responses.

Follow the [sequence diagram](Design.md#create-analysis-sequence).
Explain why a timeout does not undo data component C already stored.

## 6. Test behavior as you build

Run:

```powershell
.\.venv\Scripts\python.exe tests\test_store_sql.py
.\.venv\Scripts\python.exe tests\test_flow.py
```

The corrected version passes one direct SQL test and ten HTTP tests.
[The coverage table](Verification.md#test-results) says what
each checks. Tests of allowed requests are important alongside attack tests.

When practising, cover login, normal creation/list/read, another user's
denied read, admin deletion, wrong/expired/changed tokens, large input,
untrusted owner fields, and SQL injection.

Invalid-password, malformed-JSON, missing-token-field, wrong-analysis-ID,
and invalid-result tests would be useful additions. The current suite
does not check every one of those cases.

## 7. Reproduce the controlled vulnerability experiments

Use [Vulnerability_Experiments_Guide.md](Vulnerability_Experiments_Guide.md).
A test must reach its intended assertion for a failure to demonstrate the flaw.

The saved results show:

- Missing size check: large input accepted, then rejected after correction.
- Missing owner check: Bob reads Alice's result, then is denied after correction.
- SQL built from input: the HTTP experiment returns Alice's record on the
  vulnerable branch, while the corrected route rejects the injected ID. The
  direct SQL regression returns no record after parameterization.
- Composition flaw: a token permitting creation for Alice is used to store
  the result for Bob. Corrected component C rejects the body owner.

Use the `vulnerable-version` branch for the combined vulnerable version and
the `fixed-version` branch for the corrected application. The current
comparison commits are `a1928f4` and `1ccd085`. Some older attempts cannot
repeat their saved results unchanged. The experiment guide explains why.

The combined version removes both owner-on-write and owner-on-read protections.
Its wrong-owner response proves the incorrect write, but the later read does
not isolate the composition flaw's effect. Keep that limit in your explanation.

## 8. Understand and finish the CI gates

Read the `Jenkinsfile` and
[Verification](Verification.md#jenkins-evidence-and-gaps).

Jenkins runs package installation, helper build, source checks, package
advisory checks, tests, and report saving. A gate is a rule that makes the
build fail when a required check fails.

Build commands use separate Jenkins steps. The test stage checks all three
suite exit codes. The dependency gate checks the approved installed inventory,
and HTTP tests use separately allocated ports. Local tests verify the gate
and concurrent HTTP runs. New Jenkins runs and complete automatic
push/pull-request evidence still need to be saved.

The current Jenkinsfile uses `python` from the Windows service PATH.
The console shows its path and version. Check these before investigating
application errors.

## 9. Explain and hand over the result

Use the [report source map](Requirements_Traceability.md#report-source-map).
Explain the application purpose, service boundaries, flow of permission,
three principles, four experiments, observed tests/scans, security gates,
remaining limits, and production needs.

For each function, identify its inputs, what is trusted, what is rejected,
what changes it makes, and which test checks it. Practise explaining it
without reading the code.

Use the
[completion checklist](Verification.md#remaining-work)
for actual unfinished work.
