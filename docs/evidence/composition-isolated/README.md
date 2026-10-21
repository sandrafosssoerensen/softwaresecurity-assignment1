# Local evidence for the isolated composition comparison

The [experiment explanation](../../Composition_Isolation.md) describes the
scenario, assumptions, and exact commands. These files contain local test
output from Python 3.12.10. They are supplementary evidence alongside the
historical Jenkins archives.

| Version | Source commit | Dependency gate | Direct SQL | Ordinary HTTP suite | Focused composition test |
|---|---|---|---|---|---|
| `fixed-version` | `10107b4` | 6 pass, exit 0 | 1 pass, exit 0 | 10 pass, exit 0 | 1 pass, exit 0 |
| `experiment-composition-isolated` | `c43ebf8` | 6 pass, exit 0 | 1 pass, exit 0 | 9 pass and 1 expected failure, exit 1 | 1 expected failure, exit 1 |

| Suite | Corrected output | Isolated vulnerable output |
|---|---|---|
| Dependency gate | [fixed-dependency.txt](fixed-dependency.txt) | [isolated-dependency.txt](isolated-dependency.txt) |
| Direct SQL | [fixed-sql.txt](fixed-sql.txt) | [isolated-sql.txt](isolated-sql.txt) |
| Ordinary HTTP | [fixed-flow.txt](fixed-flow.txt) | [isolated-flow.txt](isolated-flow.txt) |
| Focused composition | [fixed-focused.txt](fixed-focused.txt) | [isolated-focused.txt](isolated-focused.txt) |

Each focused output includes a `COMPOSITION_OBSERVATION` JSON object with
the actual response codes, the delegated permission's user/action/resource,
and the observed owner. It does not include raw credentials.

Both focused runs first confirm that Bob receives 404 for Alice's ordinary
record. Only the isolated vulnerable run accepts a new document for Bob using
Alice's create permission. Alice then receives 404 and Bob receives 200 for
that exact new ID. Thus the incorrect ownership assignment is demonstrated
while the read ownership check remains active.

The failure in the focused vulnerable output is the secure expectation
`201 != 400`. The ordinary vulnerable suite fails only
`test_untrusted_owner_field_cannot_change_owner`. Startup failures and token
validation errors did not cause these failures.

The isolated branch differs from the fixed source only in the create handler
in `app/views.py`. Inspect the patch using `git diff 10107b4 c43ebf8`.
The fixed and isolated tests used separate fresh environments and ran in
parallel on separate allocated ports.
