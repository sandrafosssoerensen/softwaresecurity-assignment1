# SSDLC plan and implementation status

SSDLC means Secure Software Development Life Cycle: planning, building,
testing, and preparing to operate software while considering security
throughout.

The original plan was committed in `8e1b610`, before the implementation
commit `7f04cee`. The tables below show the plan alongside the current status.

View the original:

```powershell
git show 8e1b610:docs/SSDLC_Plan.md
```

[Terminology](Terminology.md) explains terms such as gate, artifact, and CI/CD.

## Scope

Component A checks users' identities and coordinates requests. Component B checks and processes
an alert using the installed helper package. Component C stores analyses and checks
who may access them. They run as separate programs and communicate through
HTTP. Creation uses Component A, Component B, and Component C in sequence. Listing, reading, and deletion use Component A and Component C.
Component A and component C have separate database files.

Setup creates alice and bob as ordinary users and admin as administrator.
Users may read their own results. Admin may read all results and delete
them. The interface is an API. Registration, website pages, background jobs,
and public hosting are outside this small prototype's scope.

The processor returns a development stub: a fixed-format result used in
place of a real model. The original plan mentioned later Ollama integration,
but this was not implemented and is not required by the assignment.
The demonstrated setup uses separate local processes. Containers are an
optional setup that has not yet been tested.

## Four phases and gates

A *gate* is a rule deciding whether work may continue or be released. For
example, “all required authorization tests must pass” is a testing gate.

| Phase | Planned work and decision | Current status |
|---|---|---|
| Requirements | Define operations, data to protect, service boundaries, permissions, threats, and controls before coding. | The original plan/design were committed first. [Design](Design.md) gives the current explanation. |
| Implementation/build | Build three services, install the helper, make setup repeatable, and reject unapproved packages or files. | Services and helper work. The new dependency-approval stage checks installed names and exact versions before application tests. |
| Testing | Use fresh test data, check allowed/denied requests, demonstrate flaws, and repeat tests after fixes. Required failures must stop release. | Local corrected runs pass 17 tests including six gate tests, one direct SQL test, and ten HTTP tests. The vulnerable application still fails four HTTP tests and one direct SQL test. Tests use separate allocated ports, and Jenkins checks each suite's exit code. |
| Release/deploy/operation | Review the report/evidence and explain what production operation would need. | Production needs are documented. The final report and handover checks remain. No production deployment was performed. |

## Asset, threat, control, activity, evidence, and gate

Read this chain as: what needs protection, what could happen, how to prevent
it, what work to do, how to check the result, and whether to allow release.

| What needs protection / possible threat | Required protection | Development activity | Test or evidence | Release decision |
|---|---|---|---|---|
| Component B's processing capacity / oversized input | Reject alert JSON above 65,536 bytes. | Add size check, temporarily remove it, then restore it. | Vulnerable version accepts with 201. Corrected version rejects with 413. | The size test must pass. No resource-exhaustion measurement was made. |
| Private analyses / another user reads them | Component C checks the owner or administrator role. | Test Alice's own read, Bob's request, and admin access. | Bob gets 200 when the check is missing and 404 after the fix. | Unauthorized access must stop release. |
| SQL queries / supplied values change query meaning | Use SQL parameters. | Compare string-built SQL with parameterized SQL. | Injected ID returns a record before the fix and no record after it. | SQL test must pass. The medium Bandit warning alone does not trigger the high-only gate. |
| Correct ownership / Component B supplies a different owner | Component C uses the user ID in Component A's signed token. | Send a request carrying Alice's permission but naming Bob in the body. Repeat with only that flaw active. | The isolated version stores owner 2 while normal read ownership checks pass. The corrected version rejects the extra field. See [isolated evidence](evidence/composition-isolated/README.md). | Storing for an unauthorized owner must stop release. |
| User/service permissions / token misuse | Check token signature, service, user, action, role, analysis ID, and expiry. | Test forged, expired, wrong-service, and wrong-action tokens. | Relevant token/permission tests pass in the fixed run. | Required authorization tests must pass. |
| Installed packages / unexpected software enters build | Declare approved packages and reject others. | Check the installed packages against an approved list. | `check_dependencies.py` accepts the approved environment and rejects an extra package. Six gate tests cover approval rules. | Any approval finding makes the stage fail. |

See [Verification](Verification.md) and the
[Jenkins evidence index](evidence/jenkins/README.md) for the saved results.
[Design](Design.md#secure-design-principles) explains complete mediation,
least privilege, and fail-safe defaults with examples.

## Jenkins implementation and release policy

The [Jenkinsfile](../Jenkinsfile) downloads the selected branch using
`checkout scm`, creates a virtual environment, installs/builds the helper,
runs source/package checks and tests, saves reports, and removes the
temporary Jenkins workspace. The Windows agent must find Python 3.12 when
it runs `python`.

The intended release rules are:

- Build, installation, and tool errors must make the build fail.
- High-severity Bandit findings make the static-analysis gate fail.
- Any vulnerability reported by pip-audit, or an error running the audit,
  makes that stage fail. This is stricter than the original proposal that
  focused on high/critical dependency findings.
- Required functional and permission tests must pass.
- Installed packages must match the approved names and exact versions in
  the three requirements files and `ci/approved-local.txt`. Unexpected,
  missing, or changed packages make the approval stage fail.
- This inventory check does not verify file contents or prevent an
  installation script from running. The optional hash-manifest exercise
  remains outside the demonstrated scope.

Two scanner findings need explanation. B105 on `Bearer` is a false
positive: it mistakes a protocol name for a password. B608 identifies unsafe
SQL in the vulnerable version. It is medium severity, below the current
high-only static gate. The SQL test checks the actual query behavior.

The Bandit report commands use `--exit-zero` to save findings without
stopping at the report step. A separate command applies the static gate.
The saved comparison has both failing vulnerable tests and passing fixed
tests. Build #10 also shows successful operation after fixing Python PATH.

## Remaining work

[Verification](Verification.md#remaining-work)
contains the complete checklist. The main remaining issues are:

- Run the updated pipeline in Jenkins on the corrected and vulnerable branches.
- Save a SQL-only failure run to demonstrate that later passing tests cannot
  hide it, then restore the corrected version.
- Complete successful automatic push and pull-request build evidence is missing.

Text/JSON reports are saved. JUnit XML and service-log reports are not
currently produced/preserved.

[Requirements traceability](Requirements_Traceability.md) connects the work
to the assignment requirements.

For production, discuss encrypted connections, separate service accounts and
file access, key replacement/cancellation, rate limits, monitoring, backups,
and a real processing model if needed. These are future operating needs.
