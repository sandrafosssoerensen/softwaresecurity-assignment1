# Verification and security evidence

Initial verification environment: Python 3.12, Django 5.2.18, PyJWT 2.15.1; helper built into a wheel and installed with pip. Three Django HTTP processes started with fresh seeded databases.

Eight integration tests passed in the initial run:
1. Create/save/read; cross-user denial; administrator read.
2. Own-only listing.
3. Ordinary deletion denial; administrator deletion; disappearance after deletion.
4. B's create authority cannot delete; result remains.
5. Expired administrator/wrong-audience token rejection; result remains.
6. Invalid signature text and unexpected owner field rejection.
7. Oversized direct B input rejection.
8. Forged token rejection.

## Final secure baseline

The secure baseline was retested after the vulnerability experiments. The final local commands were:

```powershell
.\.venv\Scripts\python.exe tests\test_store_sql.py
.\.venv\Scripts\python.exe tests\test_flow.py
```

The focused SQL test passed, and the flow test passed all 9 tests, including ownership, role, token, input-size, and untrusted-owner-field checks.

## Vulnerability experiments

The vulnerable and corrected outputs are stored in `docs/evidence/`:

| Experiment | Vulnerable evidence | Corrected evidence |
|---|---|---|
| CWE-20: missing input-size validation | `CWE-20-vulnerable.txt` | `CWE-20-corrected.txt` |
| CWE-862: missing authorization | `CWE-862-vulnerable.txt` | `CWE-862-corrected.txt` |
| CWE-89: SQL injection | `CWE-89-vulnerable.txt` | `CWE-89-corrected.txt` |
| Composition/CWE-807: untrusted ownership input | `CWE-807-vulnerable.txt` | `CWE-807-corrected.txt` |

The vulnerable versions were isolated on experiment branches or commits. The final branch contains the corrected secure controls.

## Jenkins verification

Jenkins job `software-security-assignment1-ci` successfully built `assignment-work` in build #4. The pipeline created a fresh Python environment, installed pinned dependencies, built the helper wheel, ran Bandit, ran pip-audit, applied the high-severity security gate, ran the SQL and flow tests, and archived reports.

The dependency audit reported no known vulnerabilities. Bandit reported no high-severity findings. It reported one low-severity B105 finding for the literal `Bearer` token type in `app/views.py:88`; this is a protocol response value rather than a secret, but it should be acknowledged in the final report.

The downloaded reports from Jenkins build #4 are stored in
`docs/evidence/jenkins/build-4/`.

The build used branch `assignment-work` at commit `0c981d3` and finished with
`SUCCESS`.

## Remaining limitations

The checks use the deterministic model stub and do not prove real Ollama accuracy or production readiness. Docker Compose has not been verified in this local run. Protected transport, key rotation, durable processing, monitoring, and operational model evaluation remain production requirements.
