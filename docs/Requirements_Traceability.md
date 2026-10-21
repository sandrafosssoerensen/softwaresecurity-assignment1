# Assignment requirements traceability

This checklist shows where each assignment requirement is covered and what
still needs work. Page numbers refer to `Software_Security_Assignment_I (1).pdf`.

| Assignment requirement | Where to find the implementation or evidence | Current status |
|---|---|---|
| Identify functional/non-functional requirements and data flow before implementation (p. 1) | Plan/design commit `8e1b610` precedes code commit `7f04cee`. Current explanation: [Design](Design.md). | Original plan committed before code. Design details have since been expanded. |
| Three application components run as separate processes and communicate explicitly (p. 2) | [serve.py](../scripts/serve.py), [urls.py](../app/urls.py), HTTP test setup. | Component A, component B, and component C run separately and communicate over HTTP. Fixed tests pass. |
| Components have different jobs and permissions (p. 2) | Component A handles login/tokens, component B processes alerts, component C stores/checks results. [Access matrix](Design.md#access-matrix). | Application checks exist. The processes share one Windows account, so file access is not isolated. |
| At least three functions, including one that uses all components (pp. 1–2) | Login, create, list, read, admin deletion. Create uses component A → component B → component C. | Implemented and tested. |
| Own helper declared and installed as a dependency (p. 2) | [pyproject.toml](../helper/pyproject.toml) and wheel installation in [README](../README.md) and Jenkins. | Component B uses the installed `alert_helper` package. |
| Authentication, two roles, two ordinary users, one privileged user (p. 3) | Django login and [setup script](../scripts/setup_lab.py): alice/bob/admin. | Login, owner access, and role tests recorded. |
| Permission is restricted by service, resource, action, and time (p. 3) | [Token explanation](Design.md#authentication-and-authority-binding), [security.py](../app/security.py), views/store. | Implemented. Selected incorrect-token and access cases tested. |
| Three secure design principles with decisions and evidence (p. 3) | [Principles table](Design.md#secure-design-principles). | Complete mediation, least privilege, and fail-safe defaults explained with tests. |
| Three deliberately planted flaws from the course catalogue (p. 1) | CWE-20, CWE-862, CWE-89 on the current `vulnerable-version` branch. See [results](Verification.md#vulnerability-evidence). | Local comparison tests show the effects. Check the three entries against the private course catalogue. |
| One additional flaw caused by service composition (p. 1) | Component C accepts body owner instead of the token's user ID. [Isolated comparison](Composition_Isolation.md) and [local output](evidence/composition-isolated/README.md). | Wrong-owner storage and later access demonstrated with normal read checks active. Corrected request rejected. Only the owner-field test fails in the isolated ordinary HTTP suite. |
| Four-phase plan committed before implementation (pp. 4–5) | `8e1b610` and [SSDLC plan](SSDLC_Plan.md). | Commit order verified. |
| Jenkins builds/checks components and runs source/package analysis (p. 5) | Helper build, Bandit, pip-audit, [saved reports](evidence/jenkins/README.md), and build #10 console. | Successful run. Scan scope and package-version limits are explained in Verification. |
| Reject unexpected/unapproved artifacts (p. 5) | [Approval script](../scripts/check_dependencies.py), exact requirements, and `ci/approved-local.txt`. | Clean 46-package environment accepted. Extra `pypdf` rejected locally. This checks inventory, not file contents. |
| Fresh environment for functional and permission tests (p. 5) | Temporary data, keys, and component A, component B, and component C processes in [HTTP tests](../tests/test_flow.py). | Ten HTTP tests and one direct SQL test pass locally on the corrected version. Each run has separate allocated ports. Two simultaneous HTTP suites also pass. |
| Save test/analysis output files (p. 5) | Current local evidence contains test, scan, and dependency reports. The historical Jenkins folders contain five files per saved version. See the [index](evidence/jenkins/README.md). | Present locally. Latest complete Jenkins console/artifact export still needed. JUnit XML is not generated or required. |
| Define failures that stop release and make Jenkins fail on them (p. 5) | [Gate policy](SSDLC_Plan.md#jenkins-implementation-and-release-policy). | Separate build steps and explicit checks of every test-suite exit code. Verify the updated behavior in Jenkins, including a SQL-only failure run. |
| Run Jenkins for every push and pull request (p. 5) | #9 shows push delivery. Multibranch discovery and `githubPush()` configured. | Save a successful automatic push build and a pull-request build. |
| Explain production release/operation needs (p. 5) | [Production discussion](Design.md#production-release-and-operation). | Supporting material ready for the report. |
| README explains purpose and exact build/seed/run/test commands (p. 6) | [README](../README.md), [How to run](How_To_Run.md). | Updated for the scripts and branches used here. |
| Include source, history, design/threats/access matrix, pipeline, helper (p. 6) | Files and Git history in this repository. | Present locally. Final remote access/history check needed. |
| Separate report with evidence links (p. 5) | [Report source map](#report-source-map). | Still to write: 2,000–2,500 words excluding the supporting material listed by the assignment. |
| AI-use declaration (p. 6) | [AI declaration](AI_Use.md). | Assistance described. Check the declaration before submitting. |

## Scope decisions

The assignment allows separate local processes and an API client. Docker,
Ollama, website pages, and ZAP are not required. The development result is
clearly labelled as a stub, meaning a simple replacement for a real model.
The optional container configuration has passed a local Rancher Desktop
smoke test covering image builds, three running components, health checks,
and the authenticated create/read/delete flow. See
[Docker evidence](evidence/docker/README.md).

The ordinary helper package is required and installed. The malicious
package exercise and its digest-manifest experiments are optional and were
not performed. A digest is a value used to check whether file contents
changed. The separate required build rule about rejecting unapproved
artifacts still applies.

## Report source map

Use these documents to understand the work, then explain the decisions and
results in your own words in the final report.

| Report topic | Source |
|---|---|
| Purpose, scope, and requirements | [Design](Design.md#purpose-and-requirements) |
| Data flow, tokens, services, and permissions | [Design](Design.md), including sequence diagram and access matrix |
| Three security principles | [Design principles](Design.md#secure-design-principles) |
| Original plan and work in each phase | [SSDLC plan](SSDLC_Plan.md) and commit `8e1b610` |
| Four flaws, prerequisites, observed effects, and fixes | [Experiment guide](Vulnerability_Experiments_Guide.md) |
| Tests, scans, and release decisions | [Verification](Verification.md), [Jenkins reports](evidence/jenkins/README.md) |
| Changes needed before production use | [Production discussion](Design.md#production-release-and-operation) |
| AI assistance | [Declaration](AI_Use.md), checked by the author before submission |

See the [completion checklist](Verification.md#remaining-work)
for the remaining tasks.
