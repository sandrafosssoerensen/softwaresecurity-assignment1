# Minimal V1 Design

## Functions and components

A: authenticate seeded users, issue signed authority, forward analysis requests, list/read/delete through C. B: verify one analysis request, use installed helper, produce and validate one result, store through C. C: own analysis database and enforce owner/admin/action checks. Databases do not count as components.

All operations are synchronous. Analyses are saved before the response reaches the user. No job status API. A model failure returns an error without a completed result. Timeout handling is a lab limitation to record, not a background-job feature.

## Access matrix

| Operation | Ordinary user | Administrator | B result token |
|---|---|---|---|
| Request analysis | Yes | Yes | No |
| List/read results | Own | All | No |
| Create stored result | Through assigned B request | Through assigned B request | Assigned ID and owner only |
| Delete result | No | All | No |

## Assets and STRIDE

Assets: alerts/results/ownership, credentials, usable tokens, private signing key, model capacity. Boundaries: client–A, A–B, A–C, B–C, model output–B, installed helper–B.

S: forged/stolen tokens; signature and claims validation; bearer-token theft remains a limitation.
T: changed owner/results/SQL; owner binding and parameterized queries.
R: ordinary diagnostic/test logs aid investigation; no dedicated audit system or non-repudiation claim.
I: cross-user disclosure; C owner/admin checks and safe errors.
D: oversized/slow model input; input limit and timeout; no claim of general DoS prevention.
E: administrator/service authority misuse; scoped per-analysis permissions, B cannot delete.

## Input and output

Required selected alert fields: event_type=alert, timezone timestamp, valid source/destination IP, nonblank protocol, positive signature_id, nonblank signature, severity 1–3. Ports optional, integers 0–65535 when present. Extra event fields allowed but not sent to the model. Helper validates and selects fields. B enforces 64 KiB compact UTF-8 JSON limit.

Output: observation, interpretation, uncertainty (nonblank strings), recommended_actions and evidence_fields (nonempty string lists). Evidence references must exist in selected input. Shape validation does not prove accuracy. Store original/selected alert, owner, model/prompt/settings/timing and output. UUID analysis ID is an identifier, not authorization.

## Planned tests and experiments

Functional create/list/read/delete; own vs other user; ordinary vs admin; direct C attempts; B deletion denied; forged/expired/wrong audience tokens; malformed/oversized alerts; helper error; model schema error; model stub for deterministic tests.

Three catalogue experiments: CWE-20 omitted size check, CWE-862 omitted C ownership check, CWE-89 unsafe interpolation in C query. Fourth composition experiment: vulnerable C accepts B's unverified owner field. Corrected C uses verified claims. Test reachability and actual effects with unrelated controls enabled. Use controlled lab fixtures, correct and retest. No experiment result is claimed yet.

## Production discussion only

Protected transport, credential/key rotation and revocation, backups/retention, durable processing, monitoring, dependency updates, and LLM evidence/accuracy evaluation with human review. These are not new prototype features.
