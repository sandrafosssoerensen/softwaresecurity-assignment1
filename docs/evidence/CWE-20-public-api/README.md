# CWE-20 through the public API (manual test)

The automated regression test `test_size_limit_direct_b` sends an oversized
alert directly to component B. This manual test checks the path an ordinary
user would take: through component A's public `POST /analyses` route.

## Procedure

1. Start components A, B, and C as normal servers on ports 8000–8002, as in
   the README.
2. Log in as `bob`, an ordinary user.
3. Send the example alert with an extra `padding` field of 66,000 characters
   (66,287-byte request body) to `POST /analyses` on component A.
4. Read the access logs of components B and C.

The request body is below Django's 131,072-byte limit, so component A accepts
it and forwards the alert to component B. The 65,536-byte processing limit is
enforced only by component B.

## Results

| | `vulnerable-version` (`7b082c2`) | `main` (`256ac40`) |
|---|---|---|
| Response to bob | 201, analysis stored | 413 `INPUT_TOO_LARGE` |
| Component B log | `POST /internal/analyze` 201 | `POST /internal/analyze` 413 |
| Component C log | `POST /internal/analyses` 201 | No request reached C |

- [vulnerable-version.txt](vulnerable-version.txt): full output for the vulnerable version.
- [corrected-main.txt](corrected-main.txt): full output for the corrected version.

The application code on `256ac40` is identical to the code built by the
saved Jenkins builds.

## Repeating the test

[manual_cwe20.sh](manual_cwe20.sh) runs the procedure from Git Bash on
Windows. Use a separate checkout of the version to test, so the script's
`setup_lab.py` call does not change your own `.runtime` data, and make sure
ports 8000–8002 are free:

```bash
bash docs/evidence/CWE-20-public-api/manual_cwe20.sh <checkout> "<label>" <path-to-python>
```

The Python environment must contain the packages from `requirements.txt` and
the installed `alert-helper` wheel.
