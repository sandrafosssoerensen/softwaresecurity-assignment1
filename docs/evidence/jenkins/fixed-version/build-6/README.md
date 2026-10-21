# Jenkins evidence for fixed-version build 6

Result: **SUCCESS**.

The complete `console.txt` records automatic branch indexing, checkout of
revision `25f56d63d4660b17b910bdf670ed8355293af18c`, every pipeline stage,
artifact archiving, and the final successful result.

The extracted artifact files are:

- `dependency-approval.json`
- `bandit.json`
- `bandit.txt`
- `pip-audit.json`
- `test_dependency_gate.txt`
- `test_store_sql.txt`
- `test_flow.txt`

The dependency suite passes six tests, the direct SQL suite passes one test,
and the HTTP suite passes ten tests. Dependency approval has no findings,
pip-audit reports no known vulnerabilities, and the Bandit high-severity gate
passes. Bandit records one low-severity B105 warning because it mistakes the
`Bearer` token-scheme name for a password. The value is not a credential.
No credential material was found in the saved files.
