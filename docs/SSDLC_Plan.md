# SSDLC plan and implementation status

The original four-phase plan is preserved in commit `8e1b610`
(`Document minimal scope and initial four-phase SSDLC plan`), before feature
implementation in `7f04cee`. This file now records the plan and subsequent
status; later additions must not be represented as decisions recorded earlier.

To inspect the original:

```powershell
git show 8e1b610:docs/SSDLC_Plan.md
```

## Scope

Three Django processes communicate over HTTP. A handles authentication and
coordination, B validates/processes one alert using the installed helper, and
C owns analyses and enforces resource access. A → B → C creates a result;
A → C lists, reads, and deletes. A and C use separate SQLite files.

Two ordinary users and one administrator are seeded. Ordinary users access
their own analyses; an administrator can access all and delete. The interface
is an API. Registration, a GUI, background jobs, public hosting, and the
optional malicious supply-chain exercise are outside the chosen scope.

The current processor is a labelled deterministic stub. The original plan
anticipated later Ollama integration, but no such integration is implemented
or required by the supplied assignment. Docker Compose is an unverified
optional configuration; separate local processes are the documented run mode.

## Four phases and gates

| Phase | Planned deliverable and gate | Current status |
|---|---|---|
| Requirements | Scope, operations, assets, boundaries, access matrix, STRIDE, and principles reviewed before implementation. | Original plan/design committed first; current details in [Design](Design.md). |
| Implementation/build | Three components and an installed helper; repeatable build; reject unexpected/unapproved dependencies or artifacts. | Components/helper implemented; dependency approval enforcement is still missing. Version pins do not provide that gate by themselves. |
| Testing | Fresh functional/authorization tests; malformed input rejection; demonstrate and correct vulnerabilities; required failures block release. | Nine HTTP tests and one SQL test pass in saved evidence. Composition demonstration and reliable CI failure propagation remain open. |
| Release/operation | Document production needs and review evidence, report, and AI declaration before submission. | No production deployment. Final report, author review, and submission checks remain. |

## Asset → threat → control → activity → evidence → gate

| Asset/threat | Control and lifecycle activity | Evidence | Gate decision |
|---|---|---|---|
| Processing capacity / oversized input | Implement B's 64 KiB compact UTF-8 alert limit; remove/restore it in an isolated test. | CWE-20 logs show 201 in vulnerable mode versus expected 413 after correction. No model-call/resource-usage measurement was made. | Corrected test must reject the request. |
| Analysis confidentiality / missing authorization | Enforce owner/admin checks at C; test cross-user reads and legitimate access. | CWE-862 logs show Bob receiving 200 versus corrected 404. | Unauthorized disclosure blocks release. |
| Query integrity / SQL injection | Use parameterized SQL; compare a direct storage-query test with the unsafe variant. | CWE-89 logs show an injected ID returning a record versus corrected `None`. | SQL regression must pass; do not claim the UUID-filtered HTTP route was exploited. |
| Ownership integrity / composition | Bind ownership to C's verified token, not a body field supplied across B–C. | Corrected rejection passes; vulnerable log fails before the attack request. | Open: reproduce actual wrong-owner storage/read and corrected denial. |
| Authority / token misuse | Fixed algorithm, issuer/audience/expiry/scope/role checks and per-resource bindings. | Forged/expired/wrong-audience and create-token-delete tests. | Required authorization tests must pass. |
| Dependency trust / unexpected artifacts | Declare installations and enforce an approved dependency inventory. | Requirements files and helper wheel exist; no inventory comparison/integrity gate yet. | Open: enforce rejection and demonstrate it. |

Complete mediation, least privilege, and fail-safe defaults are mapped to
implementation and tests in [Design](Design.md#secure-design-principles).

## Jenkins implementation and release policy

The intended policy is to build/test pushes and pull requests, use fresh
test data, preserve results, and fail on required security violations.
The existing [Jenkinsfile](../Jenkinsfile) performs:

- checkout and a new virtual environment;
- application/build dependency installation and helper wheel build/install;
- Bandit report generation for `app/` using `--exit-zero`;
- pip-audit for `requirements.txt`;
- a separate Bandit `-lll` gate for high-severity findings;
- the SQL and HTTP test commands, then report archiving and workspace cleanup.

The actual dependency-audit command fails on reported vulnerabilities without
a severity filter. It does not implement the earlier proposed
high/critical-only dependency policy. The reviewed low-severity Bandit B105
finding for `Bearer` is recorded in [Verification](Verification.md).

The following must be resolved before claiming the complete policy works:

1. Multi-command Windows `bat` blocks do not explicitly stop after each failed
   command. A SQL-test failure followed by a passing flow test can be hidden.
   Split commands into checked steps or propagate each nonzero exit status,
   then record a failing-control build and a passing corrected build.
2. Application/build versions are listed, but `pip`, Bandit, pip-audit, and
   some resolved dependencies are not fully pinned. No automated approval
   inventory/hash comparison exists. Implement the required rejection gate.
3. Bandit currently scans only `app/`; the helper/scripts are outside that
   scan. pip-audit targets runtime requirements, not the complete build-tool
   environment. Document or expand the chosen analysis scope.
4. A successful multibranch scan was shown, but no push-triggered and
   PR-triggered build evidence is saved here. Periodic scans may combine
   multiple pushes; they do not prove a build for every push.
5. Report files are archived when created. The test harness deletes temporary
   service logs, produces no JUnit XML, and missing artifacts are allowed by
   the pipeline. Do not claim those additional artifacts exist.

Build #4 artifacts show a successful recorded run of both test suites and
the scanners. They do not establish that failing controls or triggers were
tested. Full details and evidence links are in [Verification](Verification.md).

## Remaining submission work

[Requirements traceability](Requirements_Traceability.md) is the checklist
for assignment coverage. Preserve runnable CWE-862/CWE-89 variants with
revision-linked output (the current historical snapshots have discrepancies).
Complete the composition evidence and CI gates/
trigger evidence above, confirm the three chosen entries against the course
catalogue, and write the 2,000–2,500-word report with code/commit/test references.
Review [AI_Use.md](AI_Use.md) personally and preserve full Git history.

TLS, key rotation/revocation, separate OS identities, monitoring, backups,
and production analysis quality are discussion items, not implemented features.
