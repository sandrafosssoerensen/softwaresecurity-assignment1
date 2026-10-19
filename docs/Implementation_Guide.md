# Learning guide: rebuild the application from an empty repository

This is a learning exercise for reproducing and understanding the existing
project. It deliberately starts from an empty repository; it does not mean
the current repository is empty or that every task below is unfinished.

For running the existing application, use [How to run](How_To_Run.md).
For the actual completion status, use
[Requirements traceability](Requirements_Traceability.md) and
[Verification](Verification.md). In particular, the current composition
demonstration and CI gates still have open items.

Work in a separate learning directory/repository if you reproduce the code.
Preserve the assignment repository and its original history.

## 1. Understand the scope before coding

The supplied assignment requires three separate communicating processes,
authentication, authorization, at least three functions, two ordinary users,
one privileged user, and a project-owned helper installed as a dependency.
One function must involve all three components.

It also requires three catalogue vulnerabilities and a distinct composition
vulnerability with evidence, a pre-implementation four-phase SSDLC plan,
Jenkins build/analysis/tests/artifacts on pushes and PRs, release gates, a
2,000–2,500-word report, an AI-use declaration, and full Git history.

The chosen domain is synthetic IDS-alert processing:

```text
Submit alert → validate and summarise → store protected result → read result
```

The current processor is a labelled deterministic stub. The assignment does
not specifically require Ollama, a GUI, or Docker. The malicious supply-chain
exercise is optional; the benign installable helper is required.

Read [Design](Design.md) and explain these rules in your own words:

- Alice and Bob can create analyses and access their own results.
- Admin can access all results and delete.
- B receives authority for one processing job and one C create operation.
- C enforces resource permissions even when a request comes from another service.
- A database or helper module does not count as an application process.

## 2. Write the plan and design

For a fresh learning implementation, commit the plan before feature code.
For the existing assignment, the original plan is already in `8e1b610`;
do not rewrite history to suggest later decisions occurred earlier.

Record functional/non-functional requirements, data flow, assets, trust
boundaries, an access matrix, STRIDE threats, and at least three secure
design principles. Follow:

```text
Asset → threat → control → lifecycle activity → evidence → gate decision
```

The four phases are requirements, implementation/build, testing, and
release/operation. Define what evidence is needed to pass each phase.
[SSDLC_Plan.md](SSDLC_Plan.md) distinguishes intended gates from those
currently enforced.

## 3. Create the project structure

Use the existing files as references:

```text
app/                 Django settings, routes, views, tokens, storage
helper/              pyproject.toml and src/alert_helper/
scripts/             setup_lab.py and serve.py
examples/            request.json
tests/               test_flow.py and test_store_sql.py
docs/                design, plan, run guide, verification, and evidence
manage.py            Django command entry point
requirements.txt     application dependency versions
requirements-build.txt
Jenkinsfile
README.md
```

Container files are optional additions. Do not copy runtime keys/databases,
virtual environments, or real credentials into the learning repository.
The documented synthetic password is only for the local lab.

## 4. Install dependencies and the helper

From the new repository root, after creating the requirements and helper files:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-build.txt
.\.venv\Scripts\python.exe -m build --wheel --no-isolation helper
.\.venv\Scripts\python.exe -m pip install --no-deps helper\dist\alert_helper-0.1.0-py3-none-any.whl
```

Study `helper/pyproject.toml`: package name `alert-helper`, version `0.1.0`,
source under `src/`. The import is `alert_helper`.
`select_alert()` selects/validates alert fields; `validate_result()` checks
result shape and evidence references. B must use the installed package,
rather than a copy inside `app/`.

Pinning listed versions helps repeatability. It does not itself reject every
unlisted dependency or verify package approval/content. The current pipeline
still needs an explicit dependency approval gate.

## 5. Implement one layer at a time

### Django entry points and routing

Read `manage.py`, `app/settings.py`, `app/urls.py`, and `scripts/serve.py`.

`SERVICE` selects A, B, or C. The same code runs in three separate processes
with different routes and data directories. `settings.py` loads Django's
authentication apps/database only for A.

Explain why three server processes satisfy the architecture requirement,
whereas three classes in one process would not.

### Users and signed authority

Read `scripts/setup_lab.py`, `login()` in views, and `app/security.py`.

Setup generates RSA keys, migrates A's database, and seeds alice/bob/admin.
Django verifies passwords; A maps `is_staff` to the admin role.
A issues RS256 tokens. Verification fixes the algorithm and checks signature,
issuer, audience, expiry, required claims, scope, and role.

Explain the additional `analysis_id` checks in the views. The authority
table in [Design](Design.md) gives the actual audiences, scopes, and lifetimes.
B/C receive only public-key configuration in the normal launch, although
same-user local processes are not filesystem-isolated.

### Resource service C

Read `app/store.py` and `stored_analyses()`.

C's SQLite table has `id`, `owner`, and JSON `document` columns.
Parameterization keeps values separate from SQL syntax:

```python
db.execute("SELECT * FROM analyses WHERE id=?", (analysis_id,))
```

C's view validates token authority and binds resource IDs. The store checks
read ownership and filters lists. The view checks administrator authority
before calling `store.delete()`.

Explain why an unpredictable ID cannot replace authorization.

### Processing service B

Read `analyze()`.

B verifies execute authority, limits alert JSON size, validates selected
fields, verifies the C create token, and matches user/resource claims between
the tokens. It constructs a stub result, validates it, and sends the document
to C. C independently validates and derives ownership from the token.

Explain why a plain `owner_id` in the body would not be equivalent to a
verified claim.

### Public API A and service calls

Read `public_analyses()`, `body()`, `authority()`, `relay()`, and
`endpoint()`.

A validates the client token, allocates an ID, and delegates create to B with
limited tokens. Read/list/delete use C directly. `relay()` carries the HTTP
response back. The endpoint wrapper maps selected errors to API responses.
A timeout is not a transaction rollback guarantee.

Trace a complete request with the [sequence diagram](Design.md#create-analysis-sequence).

## 6. Test behavior as you build

The existing commands are:

```powershell
.\.venv\Scripts\python.exe tests\test_store_sql.py
.\.venv\Scripts\python.exe tests\test_flow.py
```

The saved baseline contains one SQL test and nine HTTP tests. Read the exact
[test coverage table](Verification.md#recorded-baseline-tests) before claiming
a particular behavior is tested.

When rebuilding, cover successful login/create/list/read, owner access,
cross-user denial, admin access/deletion, create-token deletion denial,
forged/expired/wrong-audience tokens, oversized input, untrusted owner fields,
and SQL injection. Use legitimate positive controls alongside denied attacks.

Additional tests worth adding include invalid-password login, malformed JSON,
missing claims, resource-ID mismatch, and malformed result schemas. These
are learning/test-extension targets, not all present in the current suite.

## 7. Reproduce the controlled vulnerability experiments

Follow [Vulnerability_Experiments_Guide.md](Vulnerability_Experiments_Guide.md).
For each, isolate the change, preserve unrelated controls, run a targeted
security assertion, save output with its revision, restore the control, and
run the same test plus a legitimate positive control.

Current status:

- CWE-20: oversized input acceptance demonstrated, then blocked.
- CWE-862: cross-user read recorded, then blocked; the cited vulnerable commit
  still has the ownership check, so a runnable variant must be preserved.
- CWE-89: direct storage-query injection recorded, then parameterized; the
  cited unsafe snapshot has a method-name typo and needs a reproducible replay.
- Composition/CWE-807: corrected rejection passes; vulnerable attempt fails
  during setup and must be repaired/rerun before claiming an exploit.

Retain commented explanatory variants if useful, but keep vulnerable behavior
inactive on the submission branch. Preserve runnable experiment versions and
actual evidence; comments or commit names alone do not demonstrate an exploit.

## 8. Understand and finish the CI gates

Read `Jenkinsfile` and compare it with
[Verification](Verification.md#jenkins-evidence-and-gaps).

The existing pipeline builds/installs, runs Bandit and pip-audit, tests, and
archives reports. Bandit scans suspicious Python patterns; pip-audit checks
known dependency advisories; the regression tests exercise application behavior.

The remaining tasks include reliable nonzero-exit propagation in Windows
batch steps, rejection of unapproved dependencies, and evidence of automatic
push/PR builds. A passing build does not show a failing control would be
blocked. Test both outcomes.

## 9. Explain and hand over the result

Use each document for a specific purpose:

| Document | Purpose |
|---|---|
| [README](../README.md) | Purpose, quick setup, and current status |
| [How to run](How_To_Run.md) | Reproducible usage and demonstration |
| [Design](Design.md) | Architecture, data flow, authority, threats, principles |
| [SSDLC plan](SSDLC_Plan.md) | Historical plan, lifecycle activities, gates |
| [Verification](Verification.md) | Actual outcomes, coverage, and gaps |
| [Traceability](Requirements_Traceability.md) | Requirement-to-evidence checklist |
| [AI declaration](AI_Use.md) | Accurate account of assistance and author review |

The final report should explain why the boundaries were chosen, how authority
travels through the workflow, the three principles, SSDLC/gates, four
experiments, evidence limits, and production needs. The report and author's
final AI declaration are still outstanding.

For each function you reproduce, identify its inputs, trusted claims, rejected
cases, side effects, and test. Then explain it without reading the code.
Use real small commits reflecting your work; do not invent earlier milestones.

For final completion use the single maintained checklist in
[Verification](Verification.md#remaining-work-before-claiming-submission-completion).
