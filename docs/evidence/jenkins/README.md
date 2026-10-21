# Jenkins evidence index

Saved reports from the corrected and vulnerable versions, with a short
explanation of the results.

## Current build evidence locations

The following folders contain the current Jenkins exports. Each completed
build folder includes its console output, generated reports, and a README that
explains the result.

| Branch or purpose | Build | Observed result | Folder |
|---|---:|---|---|
| `main` | #1 | Success, complete console and artifacts | [main/build-1](main/build-1/) |
| `assignment-work` | #13 | Success, complete console and artifacts | [assignment-work/build-13](assignment-work/build-13/) |
| `fixed-version` | #6 | Success, complete console and artifacts | [fixed-version/build-6](fixed-version/build-6/) |
| `vulnerable-version` | #5 | Expected failure, complete console and artifacts | [vulnerable-version/build-5](vulnerable-version/build-5/) |
| `experiment-composition-isolated` | #1 | Expected failure, complete console and artifacts | [experiment-composition-isolated/build-1](experiment-composition-isolated/build-1/) |
| Pull request #1 | #1 | Success, complete console, screenshots, and artifacts | [pull-request](pull-request/) |
| Jenkins settings | Current setup | Configuration screenshots complete | [configuration](configuration/) |

The red vulnerable builds are useful evidence only when their console and test
reports show the intended security-test failures. An installation or service
startup error would not demonstrate the vulnerability gate.

## Saved reports

Each current build folder contains the HTTP result, SQL result, dependency
tests, Bandit text/JSON reports, pip-audit JSON report, dependency-approval
report, and complete console output.

| Folder | HTTP tests | SQL test | Bandit | Package audit |
|---|---|---|---|---|
| [main/build-1](main/build-1/) | 10 pass | 1 passes | B105: 1 low warning, high gate passes | No known vulnerabilities, dependency approval passes |
| [assignment-work/build-13](assignment-work/build-13/) | 10 pass | 1 passes | B105: 1 low warning, high gate passes | No known vulnerabilities, dependency approval passes |
| [fixed-version/build-6](fixed-version/build-6/) | 10 pass | 1 passes | B105: 1 low warning, high gate passes | No known vulnerabilities, dependency approval passes |
| [vulnerable-version/build-5](vulnerable-version/build-5/) | 6 pass, 4 fail | 1 fails | B608: 1 medium warning, B105: 1 low warning | No known vulnerabilities, dependency approval passes |
| [experiment-composition-isolated/build-1](experiment-composition-isolated/build-1/) | 9 pass, 1 composition failure | 1 passes | B105: 1 low warning, high gate passes | No known vulnerabilities, dependency approval passes |
| [pull-request/pr-1-build-1](pull-request/pr-1-build-1/) | 10 pass | 1 passes | B105: 1 low warning, high gate passes | No known vulnerabilities, dependency approval passes |

## Code versions used to understand the comparison

| Version | Commit | Meaning |
|---|---|---|
| Main application | `bf9bad4` | Corrected application built successfully on `main` build #1. |
| Assignment branch | `4277779` | Corrected application built successfully on `assignment-work` build #13. |
| Fixed comparison | `25f56d6` | All protections are enabled and all required tests pass on build #6. |
| Vulnerable comparison | `7b082c2` | All four flaws are active and the required tests block build #5. |
| Isolated composition comparison | `07708b5` | Only the composition test fails on build #1. |

The full revisions and build causes appear in the corresponding console logs.

## What the files show

[The vulnerable HTTP report](vulnerable-version/build-5/test_flow.txt) shows:

- Bob reads Alice's result with 200 instead of being denied with 404.
- Large input is accepted with 201 instead of rejected with 413.
- A token permitting creation for Alice is used with Bob as owner in the
  body. Component C stores owner `2` and returns 201. Bob's read returns 200.

[The vulnerable SQL report](vulnerable-version/build-5/test_store_sql.txt)
shows the injected analysis ID returning the test record. The vulnerable HTTP
report also includes the API-level SQL regression. In contrast,
[the fixed HTTP report](fixed-version/build-6/test_flow.txt) passes all ten
tests and [the fixed SQL report](fixed-version/build-6/test_store_sql.txt)
passes the direct storage regression.

[The vulnerable Bandit report](vulnerable-version/build-5/bandit.txt)
flags string-built SQL as B608. This warning is absent from
[the fixed report](fixed-version/build-6/bandit.txt).
Both have B105 for `Bearer`, which is a false positive:
it names the authentication scheme rather than a password.

Both package audits show no known advisories for the versions checked at
that time. A clean package audit does not check the application's ownership
rules.

The vulnerable version has all four flaws together. Its response proves
that a result was stored for the wrong owner. Bob's successful read could
also be caused by the missing read owner check. See
[the experiment guide](../../Vulnerability_Experiments_Guide.md) for that limit.
The [isolated Jenkins comparison](experiment-composition-isolated/build-1/)
demonstrates the composition flaw with normal read ownership checks active.

## How to interpret the red and green builds

The vulnerable version is expected to fail tests that require secure
behavior. B608 is medium severity and does not trigger the current high-only
Bandit gate, so the tests provide the failures for this comparison.

The current source checks every test-suite exit code, allocates separate test
ports, and rejects unapproved package names or versions.
[Local checks](../local-ci-fixes/README.md) record how those changes were
checked before the Jenkins runs. [Verification](../../Verification.md#jenkins-evidence)
connects the evidence to the security requirements.
