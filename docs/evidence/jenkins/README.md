# Jenkins evidence index

Saved reports from the corrected and vulnerable versions, with a short
explanation of the results.

## Saved reports

Each folder contains five files: the HTTP test result, SQL test result,
Bandit text/JSON reports, and pip-audit JSON report.

| Folder | HTTP tests | SQL test | Bandit | Package audit |
|---|---|---|---|---|
| [assignment-work/build-4](assignment-work/build-4/) | 9 pass | 1 pass | B105: 1 low warning | No known vulnerabilities in the checked packages |
| [fixed-version/build-4](fixed-version/build-4/) | 9 pass | 1 pass | B105: 1 low warning | No known vulnerabilities in the checked packages |
| [vulnerable-version/build-4](vulnerable-version/build-4/) | 6 pass, 3 fail | 1 fails | B608: 1 medium warning, B105: 1 low warning | No known vulnerabilities in the checked packages |

The assignment-work scan is dated 2026-10-18. The fixed and vulnerable scans
are dated 2026-10-20. The folder names are kept as supplied. A name such as
`build-4` alone does not prove the original job/build number or commit:
those comparison folders do not include complete checkout logs.

The older assignment-work files were moved from `jenkins/build-4/` into
the branch-labelled folder in commit `a8881eb`.

## Code versions used to understand the comparison

| Version | Commit | Meaning |
|---|---|---|
| Corrected application | `e3378c6` | Protections are enabled. Later `a8881eb` adds evidence without changing the application. |
| Vulnerable application | `5e58e8f` | All four flaws are active. The source matches the failures shown in the saved reports. |
| Current Jenkins Python setting | `d67a0c2` | Finds Python through PATH. The supplied #9/#10 console logs use this commit. |

These are code references for repeating the experiment. They do not replace
missing original checkout logs for the comparison archives. Save the full
commit, date, command, build number, and reason the build started with
future exports.

## What the files show

[The vulnerable HTTP report](vulnerable-version/build-4/test_flow.txt) shows:

- Bob reads Alice's result with 200 instead of being denied with 404.
- Large input is accepted with 201 instead of rejected with 413.
- A token permitting creation for Alice is used with Bob as owner in the
  body. Component C stores owner `2` and returns 201. Bob's read returns 200.

[The vulnerable SQL report](vulnerable-version/build-4/test_store_sql.txt)
shows the injected analysis ID returning the test record. This historical
archive predates the newer HTTP SQL regression. The current local report in
`../local-ci-fixes/` records that additional API-level check.
[The fixed HTTP](fixed-version/build-4/test_flow.txt) archive contains the
older nine-test HTTP suite, while the fixed SQL report contains one passing
test. The current ten-test fixed run is in
[the local evidence folder](../local-ci-fixes/).

[The vulnerable Bandit report](vulnerable-version/build-4/bandit.txt)
flags string-built SQL as B608. This warning is absent from
[the fixed report](fixed-version/build-4/bandit.txt).
Both have B105 for `Bearer`, which is a false positive:
it names the authentication scheme rather than a password.

Both package audits show no known advisories for the versions checked at
that time. A clean package audit does not check the application's ownership
rules.

The vulnerable version has all four flaws together. Its response proves
that a result was stored for the wrong owner. Bob's successful read could
also be caused by the missing read owner check. See
[the experiment guide](../../Vulnerability_Experiments_Guide.md) for that limit.

## Console logs

The following console logs were shared during setup. They still need to be
exported into the evidence folders:

| Multibranch assignment-work build | Commit | What happened |
|---|---|---|
| #9 | `d67a0c2` | Started by GitHub push. Failed because Jenkins could not find `python`. |
| #10 | `d67a0c2` | Started manually. Found Python 3.12.10, built the helper, ran scan/test stages, saved reports, and ended with SUCCESS. |

#9 proves delivery of that push event. #10 proves a later successful manual
run after correcting PATH. Its individual test output was written to files,
so save those files alongside the console log.

## How to interpret the red and green builds

The vulnerable version is expected to fail tests that require secure
behavior. B608 is medium severity and does not trigger the current high-only
Bandit gate, so the tests provide the failures for this comparison.

These saved archives predate the CI fixes. The current source checks every
test-suite exit code, allocates separate test ports, and rejects unapproved
package names or versions. [Local checks](../local-ci-fixes/README.md)
record the new verification. Export fresh Jenkins runs before treating these
changes as demonstrated Jenkins behavior.
[Verification](../../Verification.md#jenkins-evidence-and-gaps) explains the
remaining work.
