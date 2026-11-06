# CONN-CADDY-MCP — Connector identity and release metadata

**Owner:** this repository. **Delivery:** SPECIFIED. **Acceptance:** NOT_AUDITED.

See [`requirements.md`](requirements.md) for the definition of every requirement ID this spec owns and [`status.json`](status.json) for their current delivery and acceptance state.

## Outcome

The version the `caddy_mcp` package reports at runtime (`caddy_mcp.__version__`) is the version that was released, so a deployed digest-only image identifies itself correctly in the fleet ledger and in acceptance runs.

## Requirements

| ID | Requirement | Evidence |
| --- | --- | --- |
| `CONN-CADDY-MCP-R001` | Connector reports its released version: `__version__` equals the `pyproject.toml` version, and the version bump tool updates both together. | `tests/test_version.py` |
| `CONN-CADDY-MCP-R002` | Live-config writes require confirmation: `caddy_load_config`, `caddy_put_config` and `caddy_patch_config` take `confirm`; without it (and without a client that can elicit) the call is refused with a typed message to repeat with confirm=true; with it, stdio and HTTP both succeed. | `tests/test_config_confirm.py` |

## Boundaries

The connector contract, certification and transport rules belong to scion-sdk. Release publication belongs to the repository pipeline.

## Why a new spec

The specs of this repository were read; none owns this capability. This spec states it for this connector only.

## Scope and interfaces

In scope: the rows of [requirements.md](requirements.md). Out of scope: the SDK modules and the engine, which own the shared capabilities.

## User Scenarios & Testing

### User Story 1 - Connector identity and release metadata (Priority: P1)

The version the `caddy_mcp` package reports at runtime (`caddy_mcp.__version__`) is the version that was released, so a deployed digest-only image identifies itself correctly in the fleet ledger and in acceptance runs.

**Acceptance Scenarios**:

1. **Given** the connector is configured, **When** the behaviour of row `CONN-CADDY-MCP-R001` (connector reports its released version) is exercised, **Then** `tests/test_version.py::test_reported_version_matches_the_released_package`.

### Edge Cases

- If `CONN-CADDY-MCP-R001` is not met, its proving test fails: connector reports its released version.

## Requirements

- **FR-001**: Connector reports its released version. Rows: `CONN-CADDY-MCP-R001`.

## Success Criteria

- **SC-001**: `tests/test_version.py::test_reported_version_matches_the_released_package`. Rows: `CONN-CADDY-MCP-R001`.

## Assumptions

- The external system is reachable with operator-supplied credentials.
- The SDK and engine contracts the rows cite are at the floors declared in `pyproject.toml`.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-CADDY-MCP-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
