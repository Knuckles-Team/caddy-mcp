# CONN-CADDY-MCP-SDK-CENTRALIZATION — Shared SDK capabilities in caddy-mcp

**Owner:** caddy-mcp.

See [`requirements.md`](requirements.md) for each row and [`status.json`](status.json) for its generated state.

## Purpose

caddy-mcp must use the scion-sdk capability for each concern the SDK centralizes. A connector copy of a centralized capability splits policy across the fleet.

## Why a new spec

Search: `git grep -n "SDK" -- specs` found no row that owns SDK capability use in caddy-mcp. The SDK index spec `SCION-CENTRALIZED-CAPABILITIES` owns the capabilities. This spec owns the connector side of each one.

## Requirements

- `CONN-CADDY-MCP-SDK-CENTRALIZATION-R001`: Requests use the governed SDK client.
- `CONN-CADDY-MCP-SDK-CENTRALIZATION-R002`: SDK floor and dependency set.
- `CONN-CADDY-MCP-SDK-CENTRALIZATION-R003`: Production wiring and hot path.

## Scope and interfaces

In scope: the rows of [requirements.md](requirements.md). Out of scope: the SDK modules and the engine, which own the shared capabilities.

## User Scenarios & Testing

### User Story 1 - Shared SDK capabilities in caddy-mcp (Priority: P1)

caddy-mcp must use the scion-sdk capability for each concern the SDK centralizes. A connector copy of a centralized capability splits policy across the fleet.

**Acceptance Scenarios**:

1. **Given** the connector is configured, **When** the behaviour of row `CONN-CADDY-MCP-SDK-CENTRALIZATION-R001` (requests use the governed sdk client) is exercised, **Then** a unit test shows the API client holds an httpx client and a request carries the configured credential through a mock transport Test: `tests/test_sdk_centralization.py::test_request_goes_through_the_governed_client`.
2. **Given** the connector is configured, **When** the behaviour of row `CONN-CADDY-MCP-SDK-CENTRALIZATION-R002` (sdk floor and dependency set) is exercised, **Then** pyproject.toml shows the floor and no unused requests pin Test: `tests/test_sdk_centralization.py::test_dependencies_have_no_unused_requests_pin`.
3. **Given** the connector is configured, **When** the behaviour of row `CONN-CADDY-MCP-SDK-CENTRALIZATION-R003` (production wiring and hot path) is exercised, **Then** a test builds the client with a mock transport, sees a 503 then a 200, and gets one result Test: `tests/test_sdk_centralization.py::test_transient_status_is_retried_by_the_sdk_client`.

### Edge Cases

- If `CONN-CADDY-MCP-SDK-CENTRALIZATION-R001` is not met, its proving test fails: requests use the governed sdk client.
- If `CONN-CADDY-MCP-SDK-CENTRALIZATION-R002` is not met, its proving test fails: sdk floor and dependency set.
- If `CONN-CADDY-MCP-SDK-CENTRALIZATION-R003` is not met, its proving test fails: production wiring and hot path.

## Requirements

- **FR-001**: Requests use the governed SDK client. Rows: `CONN-CADDY-MCP-SDK-CENTRALIZATION-R001`.
- **FR-002**: SDK floor and dependency set. Rows: `CONN-CADDY-MCP-SDK-CENTRALIZATION-R002`.
- **FR-003**: Production wiring and hot path. Rows: `CONN-CADDY-MCP-SDK-CENTRALIZATION-R003`.

## Success Criteria

- **SC-001**: A unit test shows the API client holds an httpx client and a request carries the configured credential through a mock transport. Rows: `CONN-CADDY-MCP-SDK-CENTRALIZATION-R001`.
- **SC-002**: Pyproject.toml shows the floor and no unused requests pin. Rows: `CONN-CADDY-MCP-SDK-CENTRALIZATION-R002`.
- **SC-003**: A test builds the client with a mock transport, sees a 503 then a 200, and gets one result. Rows: `CONN-CADDY-MCP-SDK-CENTRALIZATION-R003`.

## Assumptions

- The external system is reachable with operator-supplied credentials.
- The SDK and engine contracts the rows cite are at the floors declared in `pyproject.toml`.

## Traceability

| Label | Rows | Design section | Test ID | Evidence |
|---|---|---|---|---|
| FR-001 | `CONN-CADDY-MCP-SDK-CENTRALIZATION-R001` | [plan.md](plan.md) | T-001 | [test-spec.md](test-spec.md) |
| FR-002 | `CONN-CADDY-MCP-SDK-CENTRALIZATION-R002` | [plan.md](plan.md) | T-002 | [test-spec.md](test-spec.md) |
| FR-003 | `CONN-CADDY-MCP-SDK-CENTRALIZATION-R003` | [plan.md](plan.md) | T-003 | [test-spec.md](test-spec.md) |
