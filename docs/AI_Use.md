# AI-use declaration — draft for author review

AI assistance was used during development and documentation of this project.
This draft must be reviewed by the submitting author and adjusted to match
the assistance actually used and the work personally checked.

## Assistance used

- Discussing requirements, architecture, trust boundaries, secure design
  principles, and the initial SSDLC plan.
- Generating and explaining parts of the Django A/B/C implementation,
  authentication, scoped JWTs, database access, helper package, and stub output.
- Helping create setup/launch scripts, container configuration, and the initial
  eight HTTP integration tests.
- Helping add the composition regression (bringing the HTTP suite to nine)
  and the focused SQL regression; troubleshooting Windows test cleanup.
- Guiding Git branches/commits, vulnerability modifications, test execution,
  evidence capture, and interpretation of results.
- Helping write and troubleshoot the Jenkins pipeline, Windows Python path,
  Bandit/pip-audit stages, credentials configuration, and multibranch setup.
- Drafting and revising README, run/learning guides, design, verification,
  requirements traceability, and this declaration.
- Reviewing source, history, saved test/scan output, and the assignment during
  the 2026-10-19 documentation review. That review identified incomplete
  composition evidence, discrepancies between historical code snapshots and
  experiment logs, and gaps in CI gates/automation claims.

## Author actions and verification limits

The repository owner ran local commands/tests and vulnerability experiments,
managed Git commits and GitHub/Jenkins setup, and supplied terminal and build
output used in the discussion. A recorded Jenkins build includes nine passing
HTTP tests and one passing SQL test.

Generated explanations and completion claims were checked against source and
output where available. They were not all correct: the earlier claim that all
four vulnerable effects had been demonstrated was contradicted by the saved
composition log. [Verification](Verification.md) records the corrected status.

No claim is made that the author has independently reviewed or understood
every line, that every generated suggestion was accepted, or that AI assistance
was limited to proofreading. The author must describe their own review,
changes, understanding, and any additional AI use in the final declaration.
The final report is not yet present in this repository.
