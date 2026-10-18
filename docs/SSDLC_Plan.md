# Initial SSDLC Plan — Minimal V1

Status: initial plan, committed before feature implementation. This is a teaching prototype, not a completed submission.

## Scope

Three separate Django processes communicate over HTTP: A handles login/API, B performs one synchronous alert analysis using an installed helper package, and C owns stored analyses and resource authorization. A and C have separate SQLite files. A owns the private JWT signing key; B/C only verify signatures. A → B → C creates and saves an analysis; A → C lists, reads, and deletes.

Seed two ordinary users and one administrator. Ordinary users may list/read their own results; only an administrator may delete and may access all results. An API client is sufficient. No GUI, registration, background jobs, queue, polling, cancellation, dedicated audit system, or optional supply-chain experiments. A model stub supports deterministic development; real Ollama integration follows separately.

## Four phases and gates

| Phase | Deliverable/activity | Gate |
|---|---|---|
| Requirements | Scope, operations, assets, trust boundaries, access matrix, STRIDE, non-functional requirements, three principles, four experiment plans | Review that architecture/permissions/controls meet the assignment; commit this plan before code |
| Implementation/build | Three components, helper wheel installed as a dependency, pinned approved dependencies, repeatable commands | Build succeeds; unexpected/unapproved dependencies rejected; blocking findings resolved |
| Testing | Fresh environment with seed users; functional/authorization tests; isolated vulnerability experiments, corrections, and evidence | Required corrected-version tests pass; malformed inputs/results rejected; confirmed security violations block release |
| Release/operation | Discuss transport security, key lifecycle, backups, monitoring, updates, and model evaluation | Document production limitations; no production deployment planned |

## Asset → threat → control → activity → evidence → gate

| Asset/threat | Control | Evidence/gate |
|---|---|---|
| Analysis availability / oversized input (CWE-20) | B rejects alerts exceeding 64 KiB of compact UTF-8 JSON before invoking the model | Rejection with zero model calls; measure vulnerable-version effect; failure blocks corrected release |
| Analysis confidentiality / missing authorization (CWE-862) | C checks owner or administrator on every resource access; deletion admin only | Own/admin positive tests and cross-user/direct-C negative tests; disclosure blocks release |
| Query integrity / SQL injection (CWE-89) | Parameterized queries | Isolated unsafe-query variant with controlled test input; record real query effects and whether other controls block disclosure; confirmed injection blocks release |
| Ownership integrity / composition error | Verified owner and analysis ID bound to C create authority, not free owner field from B | Lab variant trusts B's owner field; correction rejects mismatch; wrong owner blocks release |
| Signing keys/tokens / spoofing | Private key only A; fixed algorithm, issuer, audience, expiry, required claims | Forged/expired/wrong-audience tokens rejected; failures block release |

Principles: complete mediation (every C operation checked), least privilege (B result authority cannot read/delete other resources), fail-safe defaults (invalid authority denied). Keep unrelated controls enabled in experiments and document prerequisites; do not claim failed exploits succeeded.

## Jenkins plan

## Current implementation status

The plan above describes the initial state and is preserved in the Git history. The current `assignment-work` branch now contains the secure A/B/C baseline, scoped RS256 tokens, input validation, ownership checks, parameterized SQL, nine passing flow tests, one passing focused SQL regression test, and vulnerable/corrected evidence for CWE-20, CWE-862, CWE-89, and the composition/CWE-807 experiment.

Jenkins build #4 completed successfully on `assignment-work`. The pipeline builds the helper wheel, installs dependencies, runs Bandit and pip-audit, applies a high-severity security gate, runs the tests, and archives reports. Remaining work is the final report, final evidence review, and explicit discussion of limitations such as the deterministic model stub and unverified Docker Compose run.

On each push/PR: validate/build, run Bandit and pip-audit, start fresh test environment, seed, run functional/authorization tests, archive logs/reports even on failure, clean up. Required test failures, build/scan failures, unapproved dependencies, unresolved high-severity static findings, and unresolved high/critical dependency advisories block release. Unclassified dependency findings require review. Any narrow exception requires documented evidence; required security guarantees cannot be waived.

No pipeline execution or vulnerability evidence exists at the initial planning stage. Preserve full Git history and record AI assistance. Report target: 2,000–2,500 words excluding figures/tables/references/appendices. README must contain exact build/seed/run/test commands. Finish real model integration, vulnerability variants, Jenkins, experiments, and report before submission.
