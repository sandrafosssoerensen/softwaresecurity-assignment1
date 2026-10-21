# Docker Compose smoke-test evidence

This folder records the optional container smoke test performed on
2026-10-21 from `assignment-work` at commit `288dde6`.

Rancher Desktop used the `dockerd (moby)` engine. The test demonstrated:

- successful builds of the component A, component B, and component C images
- three separately running containers on the Compose network
- component A exposed only on `127.0.0.1:8000`
- successful health responses from all three components
- successful analysis creation through component A, component B, and component C
- Alice reading her own result
- Bob receiving 404 for Alice's result
- Alice receiving 403 when attempting deletion
- the administrator reading and deleting the result
- Alice receiving 404 after the administrator deleted it

See [container-smoke-test.txt](container-smoke-test.txt) for the commands and
sanitized results. No access tokens are stored in this evidence.

This is a development smoke test. It is not a production deployment,
container-isolation assessment, load test, or encrypted-network test.
