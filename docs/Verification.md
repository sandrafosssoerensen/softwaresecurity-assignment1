# Verification and evidence

The saved Jenkins comparison passes ten application tests on the fixed
version and fails four on the vulnerable version. The updated local suite
also passes six dependency-gate tests. This page distinguishes historical
Jenkins reports, current Jenkins results, and local CI checks.

Read [Terminology](Terminology.md) for unfamiliar test and CI terms.

## Test results

The test environment uses Python 3.12, Django 5.2.18, PyJWT 2.15.1,
and the installed `alert-helper==0.1.0` package.

Run from the repository root, one command after the other:

```powershell
.\.venv\Scripts\python.exe tests\test_dependency_gate.py
.\.venv\Scripts\python.exe tests\test_store_sql.py
.\.venv\Scripts\python.exe tests\test_flow.py
```

[Fixed SQL output](evidence/jenkins/fixed-version/build-6/test_store_sql.txt)
shows one passing test. The corresponding Jenkins HTTP report shows all ten
functional and authorization tests passing.

| Test | What the passing result shows |
|---|---|
| `test_create_read_cross_user_and_admin` | Alice creates and reads her result. Bob gets 404. Admin can read it. The result is labelled as a development stub. |
| `test_list_only_owned` | Alice's list includes her result and excludes Bob's. |
| `test_delete_role_and_positive_control` | An ordinary user's delete gets 403 and leaves the record in place. Admin deletes with 204. A later read gets 404. |
| `test_b_authority_cannot_delete` | A token permitting creation in component C cannot be used for deletion. The record remains readable. |
| `test_expired_and_wrong_audience` | Component C rejects an expired token and a token intended for component A. |
| `test_invalid_signature_and_unknown_owner` | Component A rejects blank alert-signature text and an unexpected owner field. “Signature” here is an alert description, not a JWT signature. |
| `test_forged_token` | Component A rejects a JWT whose signature was changed. |
| `test_size_limit_direct_b` | Component B rejects a validly authenticated request containing 66,000 padding characters with 413. |
| `test_untrusted_owner_field_cannot_change_owner` | Component C rejects an extra owner field with 400. Bob then gets 404 for that uncreated record. |
| `test_sql_injection_via_api_does_not_return_a_record` | Normal reads work, but an injected analysis ID is rejected with 400 through Component A. |
| `test_injected_analysis_id_does_not_return_a_record` | The storage query treats the SQL payload as a value and returns `None`. |
| Supplementary `test_delegated_create_cannot_assign_another_owner` | The focused composition comparison checks normal read ownership, delegated creation, and later reads through Component A. It is run separately from the ten-test HTTP suite. |

The test setup logs in all three users. These tests do not check every
possible invalid password, missing token field, malformed request, wrong
analysis ID, repeated token use, or invalid result format.

## Vulnerability evidence

The [evidence index](evidence/jenkins/README.md) links the fixed and vulnerable
results. Individual per-CWE logs are also kept for reference.

| Flaw | Vulnerable result | Corrected result | Evidence |
|---|---|---|---|
| CWE-20: missing size check | Oversized input is accepted: 201 instead of 413. | The test passes by receiving 413. | [Vulnerable HTTP](evidence/jenkins/vulnerable-version/build-5/test_flow.txt), [fixed HTTP](evidence/jenkins/fixed-version/build-6/test_flow.txt) |
| CWE-862: missing owner check | Bob reads Alice's result: 200 instead of 404. | Bob is denied, while Alice and admin can read. | Same HTTP reports |
| CWE-89: SQL built from input text | The direct SQL test returns `known-analysis`, and the HTTP test returns Alice's selected record for the injected ID. | The direct SQL test returns no record, and the HTTP route rejects the malformed ID with 400. | [Vulnerable SQL](evidence/jenkins/vulnerable-version/build-5/test_store_sql.txt), [fixed SQL](evidence/jenkins/fixed-version/build-6/test_store_sql.txt), [vulnerable HTTP](evidence/jenkins/vulnerable-version/build-5/test_flow.txt) |
| Composition/CWE-807: request body chooses owner | With read ownership checks active, a token permitting creation for Alice is used with Bob as body owner. Component C returns 201 and owner `2`. Alice's later read is 404 and Bob's is 200. | Component C rejects the owner field with 400. No record is created, so later reads return 404. Normal create/read still works. | [Isolated comparison](evidence/composition-isolated/README.md) |

The size test shows acceptance of large input. It does not measure CPU or
memory exhaustion. CWE-89 now has both a direct storage regression and an
HTTP regression. The vulnerable GET experiment skips the UUID-format check so
the payload reaches the unsafe query. The corrected route rejects it before
the query, and the HTTP test uses Alice's own record rather than another
user's record.

The composition test creates tokens with the lab private key to simulate
Component B's legitimate permission to store an analysis for Alice. It does
not show an ordinary client obtaining that signing key. The combined
`vulnerable-version` also removes read ownership checking, which limits how
its later read result can be interpreted.

The supplementary [isolated comparison](Composition_Isolation.md) keeps read
ownership checks active. Bob gets 404 for Alice's ordinary record, but the
same user can read the new record wrongly assigned to him using Alice's
create permission. Alice receives 404 for that new record. This isolates the
incorrect ownership assignment from the separate CWE-862 flaw. Only the
owner-field test fails in the isolated version's ten-test HTTP suite. The
direct SQL test and all six dependency-gate tests pass on both versions.

## Git references

| Work | Reference |
|---|---|
| Original plan/design, followed by first implementation | `8e1b610`, then `7f04cee`. |
| Corrected application used for comparison | `fixed-version` source at `10107b4`, including the focused composition test. Historical Jenkins evidence used `e3378c6`. |
| Runnable version with all four flaws | Current `vulnerable-version` commit `a1928f4`. Historical Jenkins evidence used `5e58e8f`. |
| Isolated composition experiment | `experiment-composition-isolated` source at `c43ebf8`. Only the create handler differs from `10107b4`. |
| Jenkins change to find Python through PATH | `d67a0c2`. |
| Older individual experiments | `37e5f96` / `dd2643a` (CWE-20), `185aada` / `3e3f7f6` (CWE-862), `37646f2` / `a7039b4` (CWE-89), `96fb053` / `718aee3` (composition). |

Some older code versions cannot repeat their saved results unchanged.
The older CWE-862 commit still checks ownership. The older CWE-89 commit
misspells `execute` as `exectue`. The old
[CWE-807 log](evidence/CWE-807-vulnerable.txt) fails while preparing test
data, before the attack request. Use the newer comparison version and
reports when repeating the experiments.

```powershell
git diff fixed-version vulnerable-version -- app/store.py app/views.py
git show 8e1b610:docs/SSDLC_Plan.md
```

## Jenkins evidence

The [evidence index](evidence/jenkins/README.md) distinguishes saved reports,
local verification, current build folders, and build provenance.

The current multibranch evidence contains successful builds for
assignment-work #13, fixed-version #6, and main #1. Vulnerable-version #5 and the isolated
composition build #1 were blocked as intended. Their console logs, artifacts,
commits, and build causes are represented by the corresponding folders in the
evidence index.

### Scanner findings and release policy

| Check | What it does | Current result or limitation |
|---|---|---|
| Bandit report commands | Save JSON/text findings using `--exit-zero`. | They collect results without applying the release rule. |
| Bandit gate | `bandit -r app -lll` fails on high-severity findings. | Neither comparison has high findings. Medium B608 does not trigger this rule. |
| pip-audit | Checks required packages for known advisories. A finding or tool error makes the stage fail. | Both saved audits report no known advisories in the packages checked. |
| Dependency approval | Compare installed packages against approved names and exact versions. | A clean 46-package environment passes locally. An environment with extra `pypdf` fails. |
| Tests | Compare actual behavior with the expected secure behavior. | The updated stage collects all three suite exit codes and fails if any is nonzero. Local fixed tests pass and vulnerable application tests fail as expected. |

B105 flags `"token_type": "Bearer"` as a possible password. This is a
false positive: `Bearer` names the authentication scheme and contains no
secret. The warning is therefore recorded as a reviewed false positive.

B608 flags SQL made by inserting text into a query. The SQL test confirms
that the query can return a record for the injected ID. Bandit's severity
and confidence labels are estimates. A finding needs review.

Bandit scans only `app/`. It does not scan the helper, scripts, or tests.
pip-audit checks runtime requirements rather than every package used by
build tools. The saved clean audit describes those package versions on that
date, not all future installations.

### Failure propagation

“Failure propagation” means making sure a failed command also makes Jenkins
fail. Build commands now run in separate `bat` steps. The Tests stage uses
`returnStatus: true` for each suite, saves all three reports, and calls
`error(...)` if any suite fails. A passing HTTP suite cannot overwrite the
SQL suite's result.

Current successful and deliberately blocked Jenkins builds show that the
updated pipeline propagates required test failures. The Tests stage preserves
the status of every suite before making its gate decision. Local test output
and Jenkins output are labelled separately in the evidence index.

### Environment isolation and artifacts

Each HTTP suite uses temporary keys, users, and databases. Component C,
component B, and component A start in that order on separate loopback
ports allocated by the operating system. Each server publishes its port
only after binding, and the suite checks its service identity and health.

Two local HTTP suites ran concurrently and both passed all ten tests.
A separate concurrent fixed/vulnerable comparison preserved the intended
differences: fixed HTTP passed, vulnerable HTTP had four security failures.
`disableConcurrentBuilds()` remains useful within a branch, but is no
longer relied on to separate ports across branches.

An artifact is a saved output file. Jenkins archives generated text/JSON
reports even after failure and then clears its workspace. Empty archives
are permitted when an earlier failure prevented report creation. Tests
do not generate JUnit XML. Temporary service logs are removed after tests.

### Dependency approval

The consumer-controlled approval list consists of `requirements.txt`,
`requirements-build.txt`, `requirements-ci.txt`, and
`ci/approved-local.txt`. Every entry requires an exact name and version.
The local helper has its own approved entry outside the helper source.

The approval script checks the installed inventory after installation and
before application tests. Extra packages, missing packages, duplicate
installed distributions, or changed versions fail the stage. Conflicting
or unpinned approval entries are rejected as invalid configuration.

[Local CI checks](evidence/local-ci-fixes/README.md) include a passing
46-package inventory and an actual rejected environment containing an extra
`pypdf` package. Six unit tests cover accepted inventory, extra/missing
packages, changed versions, name normalization, and unpinned requirements.

This is an inventory gate, not a content-hash or sandbox guarantee. A
different package with the same name/version would require content
verification to detect. Installation happens before the inventory check,
so use a trusted package source and an isolated build agent. The optional
malicious-package and hash-manifest experiments are outside the demonstrated
scope.

### Push and pull-request automation

The multibranch job is configured to discover branches and pull requests
and to scan periodically. Build provenance consists of the commit, build
cause, and relevant job or webhook settings.
Periodic scanning can combine several pushes, so it does not prove that
every push caused a separate build.

## Verification coverage

- [x] Original four-phase plan committed before the implementation commit.
- [x] Three separate services, installed helper, user roles, and functional/permission tests.
- [x] Runnable vulnerable version and saved results showing all four intended failures.
- [x] Fixed comparison passes ten HTTP tests and one direct SQL test.
- [x] Source/package reports and explanation of the false-positive warning.
- [x] Build #10 finds Python through the Jenkins service PATH.
- [x] Separate build commands and check every test-suite exit code in source.
- [x] Add package/version approval and demonstrate acceptance and rejection locally.
- [x] Separate test ports and pass two concurrent HTTP suites locally.
- [x] Apply the same portable pipeline and test harness to all three working/comparison branches.
- [x] Demonstrate the composition flaw alone with read ownership checks active and save both comparison runs.
- [x] Run the updated pipeline in Jenkins on corrected, vulnerable, and isolated-composition branches.
- [x] Confirm CWE-20, CWE-89, and CWE-862 against the private Brightspace course catalogue.

The [isolated composition results](evidence/composition-isolated/README.md)
are supplementary local evidence. [Design](Design.md) explains future
production needs.
