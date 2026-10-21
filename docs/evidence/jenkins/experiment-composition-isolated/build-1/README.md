# Isolated composition build 1

Jenkins recorded the expected **FAILURE** for commit
`07708b5c33916bcac2b3d1a8fc3defb9898d1728`. Branch indexing started the
build automatically after discovering the branch and its `Jenkinsfile`.

The folder contains the complete `console.txt` and these extracted artifacts:

- `dependency-approval.json`
- `bandit.json`
- `bandit.txt`
- `pip-audit.json`
- `test_dependency_gate.txt`
- `test_store_sql.txt`
- `test_flow.txt`

The dependency gate ran six tests successfully. The SQL regression test also
passed. The HTTP suite ran ten tests and produced exactly one failure:
`test_untrusted_owner_field_cannot_change_owner`. Component C accepted an
untrusted owner value, so creation and Bob's subsequent read returned
`(201, 200)` instead of the secure `(400, 404)` result.

The ordinary cross-user read test passed. This is important because it keeps
the normal ownership check active and isolates the component-composition flaw
from CWE-862 Missing Authorization.

The dependency approval report has zero findings, and pip-audit reports zero
known vulnerabilities. Bandit reports one low-severity B105 warning for the
word `Bearer`. This is the authentication scheme name, not a hardcoded
password. There are no medium- or high-severity Bandit findings.

The console ends with `Required tests failed: approval=0, SQL=0, HTTP=1`.
Therefore, the security gate correctly blocks this deliberately vulnerable
branch because of the isolated authorization failure.
