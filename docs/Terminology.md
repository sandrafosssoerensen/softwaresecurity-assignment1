# Technical terms in plain English

Short explanations of the technical words used in the project.

## Application and network terms

| Term | Meaning in this project |
|---|---|
| Component or service | One part of the application: component A handles login/requests, component B processes alerts, component C stores and protects results. |
| Process | A program that is running. Component A, component B, and component C are three separate processes. |
| API | An interface where a client sends requests instead of clicking website buttons. |
| HTTP | The protocol used to send those requests and responses. |
| Port | A number identifying a network listener on the computer, such as 8000 for component A. |
| Route or endpoint | A path for an operation, such as `/auth/token`. |
| Request body | The data sent with a request, such as an alert written as JSON. |
| JSON | A text format for structured data, for example `{"owner_id": "2"}`. |
| Analysis ID | The identifier of a stored analysis. `{id}` in a route is a placeholder for that identifier. |
| Database | Stored records. Component A keeps user accounts in one file. Component C keeps analyses in another. |
| Stub | A simple development replacement. Component B produces a fixed-format summary instead of running a real AI model. |
| Schema | Rules for the expected fields and their types. A schema check does not prove that text is true. |
| Trust boundary | A point where data or a request comes from another component and must be checked. |
| Sandbox or isolation | Operating-system restrictions on what a process can access. The local services share one Windows account and do not have this restriction. |

## Users, permissions, and tokens

*Authentication* answers “Who are you?” Component A checks Alice's login.

*Authorization* answers “May you do this?” Component C checks whether Alice may read
a particular analysis. *Authority* means the permission granted.

A *token* is a text value presented as evidence of identity or permission.
A *JWT* is the token format used here. Its *claims* are fields such as the
user ID, allowed action, intended service, and expiration time.

A *signature* lets services check that the token was signed with the private
key and has not been changed. It does not hide the token's contents.
Component A signs tokens. The other services check them with the public key.

| Token term | Meaning |
|---|---|
| Issuer, `iss` | Who issued the token. |
| Audience, `aud` | Which service should accept it. |
| Subject, `sub` | The user ID represented by it. |
| Scope | The allowed action, such as create or read. |
| Role | Ordinary user or administrator. |
| Expiration, `exp` | The time after which it is no longer valid. |
| Bearer | The authentication scheme in `Authorization: Bearer <token>`. It is not a password. |
| Delegation | Component A gives another service permission to perform a limited task for a user. |
| Forward a token | Receive a token and pass that same token to another service. |
| Replay | Send the same request or token again. A unique token ID does not automatically prevent this. |

Example: component A creates a token permitting component C to store analysis `123` for Alice.
Component A gives that token to component B. Component B processes the alert and passes the token and result
to component C. Component C checks it before storing. This token does not permit deletion or
a change of owner to Bob.

## Dependencies and setup

| Term | Meaning |
|---|---|
| Dependency | Another package the project uses, such as Django. |
| Transitive dependency | A package installed because another package needs it. |
| Pinned version | An exact version, such as `Django==5.2.18`. |
| Unpinned version | No exact version is specified, so later installation may select a different version. |
| Resolved dependencies | The complete set of packages and versions selected by pip, including packages needed by other packages. |
| Wheel | An installable Python package file ending in `.whl`. |
| Virtual environment or venv | A separate Python package environment for the project. |
| Seed | Create known test users or data before running the application. |
| PATH | The list of folders Windows searches when you type a command such as `python`. |
| Reproducible build | A setup that can be repeated with controlled inputs. Missing version pins limit repeatability. |

## Tests, Jenkins, and evidence

| Term | Meaning |
|---|---|
| Functional test | Checks that an operation works, such as creating an analysis. |
| Authorization test | Checks that allowed users succeed and other users are refused. |
| Regression test | Checks that a bug stays fixed after later changes. |
| Assertion | An expected result in a test, such as “Bob must receive 404.” |
| Positive control | A legitimate request that should still work, such as Alice reading her own result. |
| Test fixture | The users, keys, records, and services prepared for a test. |
| Static analysis | Checking source code without exercising the application's requests. Bandit does this. |
| Dependency audit | Checking installed/required package versions against known vulnerability reports. pip-audit does this. |
| Advisory | A published notice about a known security problem in a package or product. |
| Finding | Something a scanner reports for review. It is not automatically a confirmed vulnerability. |
| False positive | A scanner warning that turns out not to be a real problem in that location. |
| Gate | A rule that stops a build/release when a required check fails. |
| Exit code | A number a command returns: usually 0 for success, nonzero for failure. Jenkins uses this to detect failures. |
| Failure propagation | Making sure a failed command also makes the Jenkins step/build fail. |
| Artifact | A saved file, such as a built package or a test report. |
| Pipeline | The automated sequence of build, scan, test, and report steps. |
| Jenkins agent | The computer/process that runs the pipeline commands. |
| CI/CD | Automated integration, checks, and delivery steps. This project runs checks. It does not deploy a production service. |
| Pull request or PR | A request to review and merge changes between Git branches. |
| Webhook | A notification sent from GitHub to Jenkins after an event such as a push. |
| Commit or revision | A saved Git version, identified by a hash such as `d67a0c2`. |
| Snapshot | The files as they existed at a particular revision. |
| Evidence provenance | Information about where a report came from: revision, job/build number, date, command, and trigger. |
| SSDLC | Secure Software Development Life Cycle: plan, build, test, and consider release/operation with security throughout. |
| CWE | A numbered category of software weakness. |

## HTTP response codes used in the examples

| Code | Meaning here |
|---|---|
| 200 | Request succeeded and returned data. |
| 201 | A new analysis was created. |
| 204 | Operation succeeded with no response body, such as deletion. |
| 400 | Request data does not meet the expected format. |
| 401 | A login or token check failed. |
| 403 | The request was understood, but permission is insufficient. |
| 404 | Record not found or not available to this user. |
| 413 | Input is too large. |
| 503 / 504 | Another service was unavailable or did not respond in time. |

For the full workflow, read [Design](Design.md). For commands, read
[How to run](How_To_Run.md).
