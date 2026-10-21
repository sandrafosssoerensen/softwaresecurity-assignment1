# Assignment requirements traceability

This matrix shows where each assignment requirement is covered. Page numbers
refer to `Software_Security_Assignment_I (1).pdf`.

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
| Three deliberately planted flaws from the course catalogue (p. 1) | CWE-20, CWE-89, and CWE-862 on the current `vulnerable-version` branch. See [results](Verification.md#vulnerability-evidence). | The course catalogue lists all three. Local comparison tests show their effects. |
| One additional flaw caused by service composition (p. 1) | Component C accepts body owner instead of the token's user ID. [Isolated comparison](Composition_Isolation.md) and [local output](evidence/composition-isolated/README.md). | Wrong-owner storage and later access demonstrated with normal read checks active. Corrected request rejected. Only the owner-field test fails in the isolated ordinary HTTP suite. |
| Four-phase plan committed before implementation (pp. 4–5) | `8e1b610` and [SSDLC plan](SSDLC_Plan.md). | Commit order verified. |
| Jenkins builds/checks components and runs source/package analysis (p. 5) | Helper build, Bandit, pip-audit, and [Jenkins evidence](evidence/jenkins/README.md). | Corrected builds succeeded and deliberately vulnerable builds were blocked. Scan scope and limitations are documented. |
| Reject unexpected/unapproved artifacts (p. 5) | [Approval script](../scripts/check_dependencies.py), exact requirements, and `ci/approved-local.txt`. | Clean 46-package environment accepted. Extra `pypdf` rejected locally. This checks inventory, not file contents. |
| Fresh environment for functional and permission tests (p. 5) | Temporary data, keys, and component A, component B, and component C processes in [HTTP tests](../tests/test_flow.py). | Ten HTTP tests and one direct SQL test pass locally on the corrected version. Each run has separate allocated ports. Two simultaneous HTTP suites also pass. |
| Save test/analysis output files (p. 5) | Local and Jenkins evidence contains test, scan, and dependency reports. See the [index](evidence/jenkins/README.md). | Jenkins archives text and JSON artifacts. JUnit XML is not generated or required. |
| Define failures that stop release and make Jenkins fail on them (p. 5) | [Gate policy](SSDLC_Plan.md#jenkins-implementation-and-release-policy). | Separate build steps and explicit checks of every test-suite exit code. Current corrected builds succeeded and the combined vulnerable build was blocked. |
| Run Jenkins for every push and pull request (p. 5) | `githubPush()`, multibranch branch and pull-request discovery, and periodic scanning are configured. [Pull-request evidence](evidence/jenkins/pull-request/README.md) records separate branch and `pr-head` checks. | Jenkins automatically built the branch, pull request, and merged `main` revision. |
| Explain production release/operation needs (p. 5) | [Production discussion](Design.md#production-release-and-operation). | Supporting material ready for the report. |
| README explains purpose and exact build/seed/run/test commands (p. 6) | [README](../README.md), [How to run](How_To_Run.md). | Updated for the scripts and branches used here. |
| Include source, history, design/threats/access matrix, pipeline, helper (p. 6) | Files and Git history in this repository. | Present in the repository and its history. |
| Separate report with evidence links (p. 5) | [Report source map](#report-source-map). | The report is a separate submission deliverable supported by the mapped repository material. |
| AI-use declaration (p. 6) | [AI declaration](AI_Use.md). | The assistance used is disclosed. |

## Scope decisions

The assignment allows separate local processes and an API client. Docker,
Ollama, website pages, and ZAP are not required. The development result is
clearly labelled as a stub, meaning a simple replacement for a real model.
The optional container configuration has passed a local Rancher Desktop
smoke test covering image builds, three running components, health checks,
and the authenticated create/read/delete flow. See
[Docker evidence](evidence/docker/README.md).

The ordinary helper package is required and installed. The optional malicious
package and digest-manifest experiments are outside the demonstrated scope.
A digest is a value used to check whether file contents changed. The separate
required build rule rejects unapproved artifacts.

## Report source map

These documents provide the source material for the separate report.

| Report topic | Source |
|---|---|
| Purpose, scope, and requirements | [Design](Design.md#purpose-and-requirements) |
| Data flow, tokens, services, and permissions | [Design](Design.md), including sequence diagram and access matrix |
| Three security principles | [Design principles](Design.md#secure-design-principles) |
| Original plan and work in each phase | [SSDLC plan](SSDLC_Plan.md) and commit `8e1b610` |
| Four flaws, prerequisites, observed effects, and fixes | [Experiment guide](Vulnerability_Experiments_Guide.md) |
| Tests, scans, and release decisions | [Verification](Verification.md), [Jenkins reports](evidence/jenkins/README.md) |
| Changes needed before production use | [Production discussion](Design.md#production-release-and-operation) |
| AI assistance | [Declaration](AI_Use.md) |
