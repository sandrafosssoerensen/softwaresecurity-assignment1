# Jenkins evidence for vulnerable-version build 5

Result: **EXPECTED FAILURE** because the security tests block the
intentionally vulnerable application.

The complete `console.txt` records automatic branch indexing, checkout of
revision `7b082c225ea5b25146eefe4eb6b220450e99f3b7`, successful setup and
analysis stages, artifact archiving, and the final blocked result.

The extracted artifact files are:

- `dependency-approval.json`
- `bandit.json`
- `bandit.txt`
- `pip-audit.json`
- `test_dependency_gate.txt`
- `test_store_sql.txt`
- `test_flow.txt`

The six dependency-gate tests pass and dependency approval has no findings.
Pip-audit reports no known vulnerabilities. The direct SQL test fails because
an injected ID returns a record. Four HTTP tests fail because the vulnerable
version permits cross-user reading, oversized input, SQL injection through
the API, and wrong-owner creation across the component boundary.

Bandit records one medium B608 unsafe-SQL finding and one low B105 warning.
The high-severity Bandit gate passes, while the behavior tests correctly stop
the build with `approval=0, SQL=1, HTTP=1`. No credential material was found
in the saved files.
