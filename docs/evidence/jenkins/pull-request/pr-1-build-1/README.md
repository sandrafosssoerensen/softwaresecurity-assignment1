# Pull request 1, Jenkins build 1

| Field | Recorded value |
|---|---|
| Pull request | #1, `Final evidence and documentation` |
| Source branch | `final-evidence-and-docs` |
| Target branch | `main` |
| Revision | `434f5df95b682ce67ad34eb95ea3ea64fffae744` |
| Jenkins job | Multibranch pull-request job `PR-1`, build #1 |
| Trigger | Automatic branch indexing after pull-request discovery |
| Result | `SUCCESS` |

Jenkins fetched `refs/pull/1/head` and ran in a workspace ending in `_PR-1`.
This distinguishes the run from the separate branch build. The GitHub
screenshot shows that both `continuous-integration/jenkins/branch` and
`continuous-integration/jenkins/pr-head` were triggered.

The dependency gate passed all six tests. The direct SQL regression passed,
and all ten functional and authorization flow tests passed. The dependency
approval report contains zero findings, and pip-audit reports zero known
vulnerabilities. Bandit reports one low-severity B105 warning for the word
`Bearer` and no medium- or high-severity findings. `Bearer` is the
authentication scheme name, not a hardcoded password.

The console records report archiving, `Secure build and tests passed`, GitHub
status notification, and `Finished: SUCCESS`.
