# Isolated composition experiment

This comparison demonstrates the ownership error between Component B and
Component C with the normal read ownership check still enabled. It separates
the composition flaw, CWE-807, from the missing read check, CWE-862.

## Versions

| Version | Application and test commit | Purpose |
|---|---|---|
| `fixed-version` | `10107b4` | Corrected application and the focused test. |
| `experiment-composition-isolated` | `c43ebf8` | The same code with only the request-body owner flaw enabled. |

These commits identify the source used for the saved local runs. Later
documentation commits may move the branch heads without changing this code.
The combined `vulnerable-version` remains the comparison with all four flaws.

The difference between the two isolated comparison versions is confined to
the create handler in `app/views.py`. The experimental handler accepts an
optional `owner_id` and stores that value instead of the user ID in the token.
The SQL query in `app/store.py`, its read ownership check, the UUID checks,
the size limit, and the token checks remain the same as the corrected version.

## What the test does

The [focused test](../tests/test_composition_isolated.py) reuses the fresh
three-process environment from the HTTP suite. Every run creates new keys,
users, databases, and separately allocated ports.

1. Alice creates an ordinary analysis through Component A, Component B, and
   Component C. Alice can read it, and Bob receives 404. This establishes that
   the normal read ownership check is active.
2. The test prepares a valid permission for Component C to create one new
   analysis for Alice. It represents the permission Component B would hold.
3. The test sends Component C a valid result with `owner_id="2"`, naming Bob,
   while the signed permission still has `sub="1"`, naming Alice.
4. Alice, Bob, and admin request the new ID through Component A using their
   ordinary login tokens. The test also checks an anonymous read and an
   attempt to delete with the create-only permission.

Only the lab test harness uses the private signing key to prepare the delegated
permission. This models a modified or compromised Component B using an
already-issued permission. It does not demonstrate obtaining a signing key
or an ordinary user forging a token. Raw tokens and private keys are not
included in the reports.

## Observed results

| Request or check | Isolated vulnerable version | Corrected version |
|---|---|---|
| Alice reads her ordinary analysis | 200 | 200 |
| Bob reads Alice's ordinary analysis | 404 | 404 |
| Create for Alice with body owner Bob | 201, stored owner `2` | 400, `INVALID_FIELDS` |
| Alice reads the attempted new record | 404 | 404 |
| Bob reads the attempted new record | 200, owner `2` | 404 |
| Admin reads the attempted new record | 200, owner `2` | 404 |
| Anonymous read | 401 | 401 |
| Delete with the create-only permission | 403 | 403 |

On the experimental version, the read check correctly follows the stored owner.
The error has already happened at creation: a permission for Alice was used to
store a record for Bob. This explains why Bob can read the new record while he
still cannot read Alice's ordinary record. The corrected version rejects the
extra field and never creates that new record.

The focused test always expects the secure result, so it fails on the
experimental version and passes on the corrected version. The ordinary HTTP
suite also has exactly one failing test on the experimental version, for the
untrusted owner field. Its other nine tests pass. The direct SQL regression
and all six dependency-gate tests pass on both versions.

## Repeat the comparison

Use the setup in [How to run](How_To_Run.md) and a clean working tree. Run
these commands from the repository root, keeping the same virtual environment:

```powershell
git switch experiment-composition-isolated
git rev-parse HEAD
.\.venv\Scripts\python.exe tests\test_composition_isolated.py
.\.venv\Scripts\python.exe tests\test_flow.py
.\.venv\Scripts\python.exe tests\test_store_sql.py
.\.venv\Scripts\python.exe tests\test_dependency_gate.py

git switch fixed-version
git rev-parse HEAD
.\.venv\Scripts\python.exe tests\test_composition_isolated.py
.\.venv\Scripts\python.exe tests\test_flow.py
.\.venv\Scripts\python.exe tests\test_store_sql.py
.\.venv\Scripts\python.exe tests\test_dependency_gate.py

git switch assignment-work
```

Inspect exactly what changed with:

```powershell
git diff 10107b4 c43ebf8 -- app/views.py app/store.py
```

The focused test supplements the existing HTTP suite. The Jenkinsfile already
runs the ordinary HTTP suite, whose owner-field test fails on the isolated
experimental branch. The focused test is run separately for this investigation.
The [saved evidence](evidence/composition-isolated/README.md) records the local
focused comparison. Jenkins evidence is indexed separately under
`docs/evidence/jenkins/`.
