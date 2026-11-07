# CONN-CADDY-MCP-SDK-CENTRALIZATION test specification

Tests use synthetic credentials and mock transports. They need no network.

| Scenario | Requirements | Expected result |
|---|---|---|
| Requests use the governed SDK client | `CONN-CADDY-MCP-SDK-CENTRALIZATION-R001` | A unit test shows the API client holds an httpx client and a request carries the configured credential through a mock transport |
| SDK floor and dependency set | `CONN-CADDY-MCP-SDK-CENTRALIZATION-R002` | pyproject.toml shows the floor and no unused requests pin |
| Production wiring and hot path | `CONN-CADDY-MCP-SDK-CENTRALIZATION-R003` | A test builds the client with a mock transport, sees a 503 then a 200, and gets one result |

## Adoption of scion-sdk 0.10.0 (`CONN-CADDY-MCP-SDK-CENTRALIZATION-R004`)

| Requirement | Test | Observation |
|---|---|---|
| `CONN-CADDY-MCP-SDK-CENTRALIZATION-R004` | `tests/test_scion_sdk_0_10_imports.py::test_every_scion_sdk_import_resolves_on_the_pinned_release` | Every `scion_sdk` import resolves on the pinned release; a removed path fails the test. |
