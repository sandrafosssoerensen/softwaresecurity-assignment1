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
- Writing and troubleshooting Jenkins configuration, Python PATH,
  Bandit/pip-audit steps, branch discovery, GitHub access, and triggers.
- Drafting and revising the README, design/threat model, SSDLC plan,
  requirement checklist, run/learning guides, results, and this declaration.
- Checking explanations against code and saved results, identifying CI
  issues, and rewriting documentation in plain English.

The assistance included generated code and text. It was more extensive than
proofreading.

## Work carried out

The repository owner ran commands, tests, security experiments, and Jenkins
jobs, configured GitHub/Jenkins, managed commits, and supplied console logs
and reports. The historical saved Jenkins reports contain nine passing HTTP
tests and one passing direct SQL test. The current local evidence contains
ten passing HTTP tests and one passing direct SQL test on the corrected
branch. The newer vulnerable local run shows four HTTP failures and one
direct SQL failure.

[Verification](Verification.md) contains the test results and known limitations.

Before submitting, add a personal description of which code and results you
checked, what you changed yourself, and any further AI use for the report.

## Before submitting

- Check that this list accurately describes the assistance used.
- Add a personal account of code review, changes, and understanding.
- Include any further AI use for the report or remaining implementation.
- Check the course/university declaration requirements linked in the assignment.
