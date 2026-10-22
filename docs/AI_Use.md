# AI-use declaration

ChatGPT/Codex was used for coding, explanations, tests, troubleshooting, and
documentation. The following list describes that assistance.

## Assistance used

AI helped with:

- Understanding the assignment, planning the three services, identifying
  trust boundaries, and writing the first four-phase security plan.
- Generating and explaining substantial parts of the Django code, login
  checks, signed tokens, database access, helper package, and development
  summary.
- Creating setup/start scripts, optional container configuration, and the
  first integration tests, which check several services working together.
- Adding SQL and ownership tests and fixing Windows process/log cleanup
  problems.
- Preparing vulnerable code versions, managing branch/commit workflows,
  collecting output, and interpreting vulnerable/fixed results.
- Adding a focused composition experiment with read ownership checks active,
  running the fixed and isolated versions locally, and documenting the evidence.
- Writing and troubleshooting Jenkins configuration, Python PATH,
  Bandit/pip-audit steps, branch discovery, GitHub access, and triggers.
- Drafting and revising the README, design/threat model, SSDLC plan,
  requirement checklist, run/learning guides, results, and this declaration.
- Checking explanations against code and saved results, identifying CI
  issues, and rewriting documentation in plain English.

The assistance included generated code and text. It was more extensive than
proofreading.

## Work carried out

The first three commits (`8e1b610`, `7f04cee`, `b2a7c7b`) were created by
the Codex agent. The plan and starter code were generated from the
repository owner's description of the system, scope, and security
requirements, and the repository owner reviewed them before continuing.
All later commits, including the vulnerability experiments, corrections,
Jenkins configuration, and evidence, were made by the repository owner.

The repository owner ran commands, tests, security experiments, and Jenkins
jobs, configured GitHub/Jenkins, managed commits, and supplied console logs
and reports. The saved Jenkins builds of the corrected branches pass ten
HTTP tests and one direct SQL test. The vulnerable build (#5) fails four
HTTP tests and the direct SQL test, and the isolated composition build (#1)
fails only the owner-field test.

[Verification](Verification.md) contains the test results and known limitations.

## Responsibility

The repository owner remains responsible for understanding the submitted
code, validating the recorded results, and providing the declaration required
by the course and university.
