# Software Security Assignment I — Alert-analysis prototype

This Python/Django teaching application accepts a synthetic Suricata alert,
validates it, produces a deterministic summary, and stores the result for its
owner. It supports login, create, list, read, and administrator-only deletion.

Three separate application processes share a codebase and communicate over
HTTP. A authenticates users and issues scoped authority; B processes alerts;
C owns the stored results and enforces access control. The database and the
installed helper package are not additional application services.

For a complete demonstration, use [How to run](docs/How_To_Run.md). For
architecture and authority flow, see [Design](docs/Design.md).

## Current status

The `assignment-work` branch contains the corrected input-size, ownership,
SQL, and token controls. Saved Jenkins build #4 reports show nine passing HTTP
tests and one passing SQL test. These are historical results, not a new run
of every future revision.

Three experiments have logs showing their intended effect: CWE-20,
CWE-862, and CWE-89. The cited CWE-862/CWE-89 snapshots do not reproduce their
logs unchanged and need new runnable variants. The composition/CWE-807 attempt has a passing corrected
test, but its saved vulnerable run stops during fixture creation and does
not yet demonstrate ownership confusion.

The remaining submission work includes completing that experiment, correcting
and verifying CI failure propagation, enforcing the dependency approval gate,
proving push/PR builds, and completing the report and AI-use declaration.
[Verification](docs/Verification.md) records the evidence and exact open items.

## Setup — PowerShell, Python 3.12

Use the repository directory containing `manage.py`, `Jenkinsfile`, and
`requirements.txt`. In the current extracted layout this is the inner
`software-security-v1/software-security-v1` directory.

For a fresh clone with repository access:

```powershell
git clone --branch assignment-work https://github.com/sandrafosssoerensen/softwaresecurity-assignment1.git
cd softwaresecurity-assignment1
```

Do not clone again if you already have the working copy. Preserve its Git
history; a GitHub source ZIP alone does not include `.git`.

Build, install, and seed:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-build.txt
.\.venv\Scripts\python.exe -m build --wheel --no-isolation helper
.\.venv\Scripts\python.exe -m pip install --no-deps helper\dist\alert_helper-0.1.0-py3-none-any.whl
.\.venv\Scripts\python.exe scripts\setup_lab.py
```

The project-owned dependency is `alert-helper` version `0.1.0`, declared in
[helper/pyproject.toml](helper/pyproject.toml) and installed separately as a
wheel. The shared views use its alert and result validators; B uses it during
processing.

Synthetic accounts are `alice`, `bob` (ordinary users), and `admin`
(privileged user). Their lab password is `Lab-only-Password-123!`.
Seed setup creates local RSA keys and A's authentication database. Repeating
setup resets these account passwords; it does not erase C's analyses.

Generated keys/databases are under `.runtime/`, excluded by `.gitignore`.
The launch script supplies the private-key path only to A. Local processes
run under the same OS user; this is not filesystem isolation.

## Run

Run each command in a separate terminal, from the repository root:

```powershell
.\.venv\Scripts\python.exe scripts\serve.py A
```

```powershell
.\.venv\Scripts\python.exe scripts\serve.py B
```

```powershell
.\.venv\Scripts\python.exe scripts\serve.py C
```

A listens on `http://127.0.0.1:8000`, B on port 8001, and C on port 8002.
Use A's `/auth/token` and `/analyses` endpoints. The
[PowerShell examples](docs/How_To_Run.md#5-use-the-application) show login,
creation, reads, denied access, and administrator deletion. Stop each
service with Ctrl+C.

## Test

No manually started servers are needed for these commands:

```powershell
.\.venv\Scripts\python.exe tests\test_store_sql.py
.\.venv\Scripts\python.exe tests\test_flow.py
```

Expected results for the corrected baseline are one SQL test and nine HTTP
tests passing. The SQL test uses a temporary database. The HTTP suite seeds
temporary users/keys/databases and starts three processes on ports
18000–18002; keep those ports free.

## Jenkins

[Jenkinsfile](Jenkinsfile) defines checkout, environment setup, helper build,
Bandit on `app/`, pip-audit on `requirements.txt`, a high-severity Bandit gate,
tests, and report archiving. It currently uses Windows `bat` steps and a
machine-specific Python path.

Saved [build #4 artifacts](docs/evidence/jenkins/build-4/) contain passing test
output, one low-severity Bandit finding, and no advisories reported by that
dependency scan. This does not prove every failure blocks the pipeline:
multi-command batch blocks need explicit failure propagation. Automatic
push/PR triggering and dependency approval also need final verification.
See [Verification](docs/Verification.md#jenkins-evidence-and-gaps).

## Documentation

- [How to run](docs/How_To_Run.md): install, start, use, test, and troubleshoot.
- [Design](docs/Design.md): requirements, data flow, permissions, threats, and principles.
- [SSDLC plan and status](docs/SSDLC_Plan.md): original planning reference, phases, and gates.
- [Requirements traceability](docs/Requirements_Traceability.md): requirements mapped to evidence and gaps.
- [Verification](docs/Verification.md): recorded results and remaining submission checks.
- [Vulnerability experiments](docs/Vulnerability_Experiments_Guide.md): changes, tests, effects, and limitations.
- [Implementation guide](docs/Implementation_Guide.md): learning path for rebuilding from scratch.
- [AI-use declaration](docs/AI_Use.md): assistance used; final author review remains.

## Scope and limitations

The processor is explicitly labelled `development-stub`; there is no live
Ollama/LLM integration or claim of meaningful threat assessment. The supplied
assignment does not require a particular model or container platform.

[compose.yaml](compose.yaml) and [Dockerfile](Dockerfile) are an optional,
unverified launch configuration. The verified evidence uses separate local
processes. The optional malicious supply-chain exercise was not performed.

This is a local HTTP lab using Django `runserver`. TLS, rate limiting,
separate OS identities, key rotation/revocation, durable jobs, audit logging,
and production model evaluation are not implemented.
