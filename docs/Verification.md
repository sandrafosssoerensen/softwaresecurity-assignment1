# Verification, evidence, and remaining work

Documentation review date: 2026-10-19. This review compared the current code,
Git history, supplied assignment PDF, and saved evidence. It did not rerun the
application, scanners, Docker, or Jenkins. Historical output remains unchanged.

The corrected baseline is implemented and has passing saved tests. The full
submission is not yet verified complete: the composition experiment and
several CI requirements still need work.

## Recorded baseline tests

The recorded environment uses Python 3.12 with Django 5.2.18 and PyJWT 2.15.1.
The helper is built as a wheel and installed into the environment.

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe tests\test_store_sql.py
.\.venv\Scripts\python.exe tests\test_flow.py
```

The [SQL output](evidence/jenkins/build-4/test_store_sql.txt) records one passing
test. The [HTTP output](evidence/jenkins/build-4/test_flow.txt) records nine.
Earlier CWE-20/CWE-862 logs contain eight HTTP tests because the composition
regression was added later.

| Test | What it demonstrates |
|---|---|
| `test_create_read_cross_user_and_admin` | Alice creates/reads; Bob's read is 404; admin reads; result is labelled as a stub. |
| `test_list_only_owned` | Alice's listing contains her record and excludes Bob's. |
| `test_delete_role_and_positive_control` | Ordinary deletion is 403; admin deletion is 204; later read is 404. |
| `test_b_authority_cannot_delete` | A C create token cannot delete directly at C; the record remains readable. |
| `test_expired_and_wrong_audience` | Expired delete authority and an A token used at C are rejected; record remains. |
| `test_invalid_signature_and_unknown_owner` | Blank alert-signature text and an unexpected owner field at A are rejected. “Signature” here is alert text, not a JWT signature. |
| `test_forged_token` | A tampered JWT signature is rejected. |
| `test_size_limit_direct_b` | A direct authenticated B request with 66,000 padding characters receives 413. |
| `test_untrusted_owner_field_cannot_change_owner` | C rejects an extra owner field (400), and Bob cannot read the uncreated ID (404). |
| `test_injected_analysis_id_does_not_return_a_record` | A direct call to the parameterized storage query treats the SQL payload as data and returns `None`. |

Successful login for all three seeded users is exercised during HTTP setup.
Invalid-password login, all missing-claim/malformed-JSON combinations,
invalid result schemas, replay, and every resource-mismatch path are not
individually covered by these ten tests. Passing tests do not establish
coverage of every security guarantee.

## Vulnerability evidence

| Experiment | Actual vulnerable observation | Corrected observation | Evidence |
|---|---|---|---|
| CWE-20 | Size regression fails with `201 != 413`: oversized alert accepted. | Eight-test run passes, including 413 check. | [Vulnerable](evidence/CWE-20-vulnerable.txt), [corrected](evidence/CWE-20-corrected.txt) |
| CWE-862 | Bob reads Alice's result: `200 != 404`. | Eight-test run passes, including cross-user denial. | [Vulnerable](evidence/CWE-862-vulnerable.txt), [corrected](evidence/CWE-862-corrected.txt) |
| CWE-89 | Injected ID returns `known-analysis` to its owner in a storage-level test. | One SQL test passes with no result for the injected string. | [Vulnerable](evidence/CWE-89-vulnerable.txt), [corrected](evidence/CWE-89-corrected.txt) |
| Composition/CWE-807 | Six tests fail creating an ordinary fixture with `400 INVALID_FIELDS`; the attack request is never reached. | Nine-test run passes, including rejection of the untrusted owner field. | [Incomplete vulnerable attempt](evidence/CWE-807-vulnerable.txt), [corrected](evidence/CWE-807-corrected.txt) |

The CWE-20 evidence demonstrates missing size validation, not measured CPU,
memory, model calls, or successful service exhaustion. The CWE-89 evidence is
at the storage layer: the HTTP handler additionally validates UUIDs and the
test retains ownership checks. It is not proof of cross-user HTTP SQL injection.

The composition evidence needs correction. Its test begins with
`original = self.create()`; that fails before the forged owner is submitted.
Commit `96fb053`, despite its message, contains active corrected C code and
commented vulnerable alternatives. It is not an executable vulnerable
snapshot. Commit `718aee3` merges that work.

To complete this experiment, preserve a runnable isolated variant, let normal
setup succeed, send a valid Alice-scoped create request carrying Bob's owner
field directly to C, and record whether Bob can read the stored result.
Then repeat with the corrected control and capture denial plus a legitimate
create/read positive control. Do not relabel the old log as a successful
exploit; add clearly identified new evidence.

Some older files contain PowerShell `NativeCommandError` wrappers around
Python unittest's stderr output. Interpret the actual assertions and final
`OK`/`FAILED` summary; the wrapper alone does not prove a failed test.

## Git references

| Work | Commit reference |
|---|---|
| Original plan, before implementation | `8e1b610` |
| Initial implementation | `7f04cee` |
| CWE-20 unsafe / restored control | `37e5f96` / `dd2643a` |
| CWE-862 vulnerable log / corrected log and formatting | `185aada` / `3e3f7f6`; both retain the ownership check |
| CWE-89 intended unsafe query / restored query | `37646f2` / `a7039b4`; the former contains a method-name typo |
| Composition test, comments, and incomplete evidence | `96fb053`, merged by `718aee3` |
| Jenkins pipeline / Python path | `698f103` / `0c981d3` |
| Saved Jenkins artifacts | `aacca35` |

Use `git show <commit>` to inspect actual changes. A commit message or
filename is not proof of the behavior claimed.

Two additional historical reproducibility problems were found:

- `185aada` adds only the CWE-862 vulnerable log; its `store.py` still
  enforces ownership. Checking out this commit alone does not reproduce
  the logged disclosure.
- `37646f2` contains the intended interpolated SQL but calls
  `db.exectue(query)` instead of `db.execute(query)`. That snapshot would
  raise an attribute error rather than produce the saved injection result.

The saved logs still record the intended CWE-862/CWE-89 effects, but they
cannot be reproduced from those snapshots unchanged. Preserve history and
add clearly identified runnable variants, with new output tied to their
revisions. The experiment guide describes the intended code changes.

## Jenkins evidence and gaps

The recorded job is `software-security-assignment1-ci`, build #4 on
`assignment-work` at `0c981d3`, reported as `SUCCESS`. The five archived
reports are saved in [evidence/jenkins/build-4](evidence/jenkins/build-4/).
The complete Jenkins console/job configuration is not included there.

[bandit.json](evidence/jenkins/build-4/bandit.json) contains zero high,
zero medium, and one low-severity finding: B105 on the literal `Bearer` in
`app/views.py` (line 88 in that scan). Inspection shows this is a token-type
response value, not a password. This finding is documented rather than removed.
Bandit scans `app/` only.

[pip-audit.json](evidence/jenkins/build-4/pip-audit.json) reports no known
vulnerabilities for its 13 resolved dependencies at the time of that run.
It is an audit of `requirements.txt`, not an audit of every build/CI package
or proof that future advisories will not appear.

The report-generation Bandit commands use `--exit-zero`. The separate
`-lll` command supplies the high-severity gate; this matches the
[Bandit command documentation](https://bandit.readthedocs.io/en/latest/man/bandit.html).
The pip-audit command has no severity filter: reported vulnerabilities cause
failure, as described in [pip-audit's exit codes](https://github.com/pypa/pip-audit#exit-codes).

### Failure propagation

The current `Jenkinsfile` places several commands in one Windows `bat`
block without checking each command's exit code. Specifically, SQL tests run
before flow tests. A failing SQL test followed by a passing flow test can leave
the batch step with a success exit code. The build-install block has the same
pattern.

A read-only local batch diagnostic during this review returned exit code 0
after an inner `exit 1` followed by `exit 0`. Jenkins's
[`bat` documentation](https://www.jenkins.io/doc/pipeline/steps/workflow-durable-task-step/#bat-windows-batch-script)
says it fails on the script's nonzero exit status. Thus the intended “every
required failure blocks release” policy is not reliably enforced by this file.
Split commands into separately checked steps or explicitly propagate failures,
then verify with a deliberately failing control.

### Dependency approval and artifacts

Requirements files pin listed application/build versions and the helper wheel
is explicitly installed. However, pip is upgraded, Bandit/pip-audit are
installed unpinned, and the Windows audit also resolves unlisted `tzdata`.
There is no installed-inventory/approval comparison. The required rejection
of unexpected/unapproved artifacts is not yet enforced; version pinning is
not equivalent to approval verification.

The pipeline archives `reports/**` when available, including test text and
analysis reports. It allows empty archives. No test currently writes JUnit
XML, despite an optional archive pattern. Temporary A/B/C logs are deleted by
the test harness and are not in the archived reports.

### Push and pull-request automation

A user-shared multibranch indexing log on 2026-10-18 showed:
`assignment-work` had a Jenkinsfile and a build was scheduled;
`main` had no Jenkinsfile; zero pull requests were processed.
That scan result alone does not prove successful automatic push/PR builds.

The job's periodic scanning configuration is external to the repository.
Periodic scans can combine several commits. A `githubPush()` declaration
alone does not prove webhook delivery, especially to a local-only Jenkins.
Capture both a push-triggered build and a PR-triggered build with their
revision/cause, and resolve triggering if the “every push and PR” requirement
is not met.

## Remaining work before claiming submission completion

- [ ] Complete composition exploit evidence, runnable vulnerable code, corrected replay, and positive control.
- [ ] Add reproducible CWE-862/CWE-89 experiment snapshots and new revision-linked output; preserve the historical logs and commits.
- [ ] Correct batch failure propagation and demonstrate a blocking failure followed by a passing build.
- [ ] Enforce and demonstrate rejection of unapproved dependencies/artifacts.
- [ ] Save automatic push and PR build evidence and the relevant configuration.
- [ ] Confirm CWE-20, CWE-862, and CWE-89 against the course's Brightspace catalogue; its contents were not available for this review.
- [ ] Produce the final 2,000–2,500-word report; no final report is present in this repository.
- [ ] Have the author review and finalize the AI-use declaration.
- [ ] Recheck the final revision, evidence links, repository access, and full Git history.

The supplied assignment does not require Docker or Ollama specifically.
The stub and unverified Compose configuration must be described honestly;
they are separate from the outstanding experiment and CI requirements.
