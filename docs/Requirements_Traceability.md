# Assignment requirements traceability

This maps the supplied `Software_Security_Assignment_I.pdf` to the current
repository, reviewed on 2026-10-19. “Recorded” means supported by saved output,
not rerun during this documentation review. This is a status checklist, not
a claim that the submission is complete.

| Requirement | Implementation and evidence | Status |
|---|---|---|
| Functional/non-functional requirements and data flow before implementation | Initial plan/design in `8e1b610`, implementation in `7f04cee`; current [Design](Design.md). | Original planning exists; current expanded documentation is retrospective. |
| Three application components in separate processes, explicit interfaces | [serve.py](../scripts/serve.py), [urls.py](../app/urls.py); HTTP suite starts A/B/C separately. | Implemented; recorded HTTP run. |
| Different responsibilities and permissions | A authenticates/signs, B processes, C owns results; [access matrix](Design.md#access-matrix). | Implemented at application/API level; shared local OS user is not isolation. |
| Three or more functionalities; one uses all components | Login, create, list, read, admin delete; create runs A → B → C. | Implemented; recorded functional tests. |
| Own helper declared and installed as dependency | [pyproject.toml](../helper/pyproject.toml), helper wheel installation in [README](../README.md) and [Jenkinsfile](../Jenkinsfile). | Implemented; B uses the installed package. |
| Authentication and at least two roles; two ordinary users and one privileged user | [setup_lab.py](../scripts/setup_lab.py) seeds alice/bob/admin; Django login; admin-only delete. | Implemented; recorded login/role tests. |
| Bind authority to service, resource, action, validity period | RS256 checks in [security.py](../app/security.py); ID/owner checks in views/store; [authority table](Design.md#authentication-and-authority-binding). | Implemented; token and access tests recorded, not every claims path covered. |
| Three secure design principles, each with decision/implementation/evidence | [Principles table](Design.md#secure-design-principles): complete mediation, least privilege, fail-safe defaults. | Documented with named tests and limits. |
| Three planted catalogue vulnerabilities | CWE-20, CWE-862, CWE-89 [logs](Verification.md#vulnerability-evidence) and [history review](Verification.md#git-references). | Intended effects recorded; CWE-862/CWE-89 snapshots need repair for reproduction; course-catalogue membership needs confirmation. |
| One additional composition vulnerability | Signed-owner correction and CWE-807 test exist; [vulnerable attempt](evidence/CWE-807-vulnerable.txt) fails during setup. | Incomplete: ownership-confusion effect not demonstrated; runnable vulnerable snapshot still needed. |
| Short four-phase SSDLC plan committed before feature code | `8e1b610`; [SSDLC plan](SSDLC_Plan.md). | Historical commit verified. |
| Build/validate and run static/dependency analysis in Jenkins | Helper build, Bandit on app, pip-audit on runtime requirements; [build #4 reports](evidence/jenkins/build-4/). | Implemented and recorded for that build; analysis scope is limited. |
| Reject unexpected/unapproved artifacts | Version requirements and wheel install exist; no approval-inventory check. | Implementation gap; not satisfied by pinning alone. |
| Fresh test environment, functional/authorization tests, saved results | [test_flow.py](../tests/test_flow.py), [test_store_sql.py](../tests/test_store_sql.py), archived text reports. | Recorded: nine HTTP tests plus one SQL test; no JUnit/service-log artifacts. |
| Define release blockers and fail on them | High-severity Bandit gate, pip-audit, test commands; [gate policy](SSDLC_Plan.md#jenkins-implementation-and-release-policy). | Partial: early failures in multi-command Windows batch blocks can be masked. |
| Pipeline runs on every push and pull request | Multibranch scan was shown; `githubPush()` exists in Jenkinsfile. | Not fully verified: save push/PR-triggered builds; polling alone may combine pushes. |
| Explain production release/deployment/operation needs | [Design](Design.md), [SSDLC plan](SSDLC_Plan.md). | Documented for the prototype; include discussion in report. |
| README with exact build/seed/run/test commands | [README](../README.md), [How to run](How_To_Run.md). | Present; commands matched to scripts in this review. |
| Source, full Git history, evidence, report, AI declaration | Source/history/evidence exist; [AI declaration](AI_Use.md) is a draft for author review. | Final report, declaration review, access check, and final revision verification remain. |

## Scope decisions

The supplied assignment allows separate processes or containers and does not
require Ollama or a particular AI model. The current processor is a labelled
deterministic stub; Docker Compose is optional and unverified.

A benign installable helper is required and present. The malicious
supply-chain attack and its optional experiments were not undertaken.
This does not remove the SSDLC requirement to reject unexpected/unapproved
artifacts in the build process.

See [Verification](Verification.md#remaining-work-before-claiming-submission-completion)
for the concrete remaining-work checklist.
