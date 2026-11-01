# CONN-CADDY-MCP-SDK-CENTRALIZATION — Implementation plan

Governing spec: [spec.md](spec.md). Rows: [requirements.md](requirements.md).

## Summary

The SDK owns every capability named in the rows (`SCION-CENTRALIZED-CAPABILITIES-R001`, `SCION-CENTRALIZED-CAPABILITIES-R003`, `SCION-CENTRALIZED-CAPABILITIES-R008`). caddy-mcp adds no module that repeats one. Each row deletes connector code and calls the SDK module.

## Technical Context

- **Language/Version**: Python 3.14 (floor 3.12)
- **Primary Dependencies**: scion-sdk, fastmcp
- **Storage**: N/A; the connector stores nothing
- **Testing**: pytest; the proof level each row names
- **Target Platform**: Linux containers
- **Project Type**: connector (MCP server)
- **Performance Goals**: N/A
- **Constraints**: one tool per API operation; shared capabilities come from the SDK
- **Scale/Scope**: 3 rows

## Constitution Check

- One owner per concept: pass. The connector owns one external system's calls, mappings and tools only.
- Connectors depend on the SDK and are called through arbora: pass.
- No ratchets: pass. The rows add no suppression.

## Project Structure

```text
caddy_mcp/api/api_client_base.py  existing
```

## Phase 0: Research

No unknowns. Each row names the code it touches.

## Phase 1: Design

### Live call path

`ApiClientBase.__init__` in `caddy_mcp/api/api_client_base.py` calls `create_http_client`. Every domain client and MCP tool calls `ApiClientBase.request`.

### Compatibility

Tool names, arguments, URL joining, error types and result shapes stay identical.

## Phase 2: Task approach

`tasks.md` holds one task line per row, producer first.

## Complexity Tracking

None. The constitution check passed.

## Build contract

The repository pre-commit hooks apply: `ruff-format`, `connector-standard`, `secrets`, `tests-fast`. Each row names its proving test. No suppression and no duplicate implementation.

## Production caller chain

1. `CONN-CADDY-MCP-SDK-CENTRALIZATION-R001`: arbora fleet.call -> `caddy_mcp_config` or `caddy_mcp_reverse_proxy` tool (caddy_mcp/mcp/mcp_config.py:60) -> caddy_mcp/auth.py::get_client -> caddy_mcp/api_client.py::Api -> caddy_mcp/api/api_client_base.py::ApiClientBase.request.
2. `CONN-CADDY-MCP-SDK-CENTRALIZATION-R002`: dependency resolution of pyproject.toml (dependencies = scion-sdk[mcp]) for the `caddy-mcp` console script and the `caddy_mcp:connector` entry point; no runtime code path.
3. `CONN-CADDY-MCP-SDK-CENTRALIZATION-R003`: arbora fleet.call -> `caddy_mcp_config` tool (caddy_mcp/mcp/mcp_config.py:60) -> caddy_mcp/api/api_client_config.py::Api methods -> caddy_mcp/api/api_client_base.py::ApiClientBase.request -> self._session built by create_http_client in __init__.

## Cross-repo seams

none. The cited owner rows are library capabilities the connector calls in process; spec.md names them.
