# Software Security — Minimal V1 Starter

This is the first implementation milestone, not the completed assignment. Three Django processes implement a synchronous A → B → C alert-analysis flow. A authenticates seeded users; B uses the separately installed helper package and a labelled development model stub; C saves analyses and enforces resource permissions.

**Implemented:** login; create/save/list/read/delete; RS256 scoped JWTs; owner/admin checks; input size/field validation; result-schema validation; separate SQLite files; 8 HTTP integration tests.

**Still required:** real Ollama integration; isolated versions and measured evidence for the four vulnerabilities; Jenkins pipeline and actual push/PR runs; dependency approval/static/dependency analysis gates; final report and complete AI declaration. The current model stub returns a fixed test response. The Docker Compose configuration has not yet been tested. Django runserver is used only for the local lab.

## Setup (PowerShell, Python 3.12)

Extract the ZIP and open a terminal in the `software-security-v1` folder. Preserve the included Git history.

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-build.txt
.\.venv\Scripts\python.exe -m build --wheel --no-isolation helper
.\.venv\Scripts\python.exe -m pip install --no-deps helper/dist/alert_helper-0.1.0-py3-none-any.whl
.\.venv\Scripts\python.exe scripts/setup_lab.py
```

Known lab accounts: `alice`, `bob`, `admin`. Password for all three: `Lab-only-Password-123!`. These are synthetic teaching accounts, never production credentials. Private keys and runtime databases are generated locally and excluded from Git and the ZIP. Only A needs the private key.

## Run three local processes

In three terminals, from the project folder:

```powershell
.\.venv\Scripts\python.exe scripts/serve.py A
.\.venv\Scripts\python.exe scripts/serve.py B
.\.venv\Scripts\python.exe scripts/serve.py C
```

A is on localhost:8000, B on :8001, C on :8002. The local-process mode exposes all three on loopback for learning/testing; Compose publishes only A.

Use an API client to POST `/auth/token` on A with JSON username/password. Use the returned access token in `Authorization: Bearer ...`. POST `examples/request.json` to `/analyses`. GET `/analyses` or `/analyses/{id}`. DELETE `/analyses/{id}` requires an admin token. POST returns 201 only after C saves the analysis.

## Test

```powershell
.\.venv\Scripts\python.exe tests/test_flow.py
```

Tests use isolated temporary databases/keys and three server processes on ports 18000–18002. Keep these ports free. No real model is needed. Tests clean up their processes. The tests themselves create/seed their temporary environment.

On Linux/WSL, use `python3 -m venv .venv` and `.venv/bin/python` instead of the Windows executable paths.

## Optional local container launch

After the setup command creates keys and A's seeded database:

```powershell
docker compose up --build
```

Docker Compose execution is pending verification. If you later use Linux containers, use a Linux-created virtual environment for host commands. Do not share a Windows virtual environment with WSL.

## File guide

- `app/urls.py`: routes selected for each process.
- `app/views.py`: request flow, token checks, model stub, and safe responses.
- `app/security.py`: A's token issuance and fixed-algorithm verification.
- `app/store.py`: C's parameterized SQLite queries and owner checks.
- `helper/`: standalone package built as a wheel and installed.
- `docs/SSDLC_Plan.md`: initial four-phase plan committed before code.
- `docs/Design.md`: minimal architecture, assets, access matrix, STRIDE, experiment plans.
- `docs/AI_Use.md`: draft declaration of AI assistance.
- `tests/test_flow.py`: integration tests.

The initial planning commit precedes the implementation commit. Preserve the complete Git history when continuing the project. Implementation status and completed checks are recorded in `docs/Verification.md`; remaining work is listed above.
