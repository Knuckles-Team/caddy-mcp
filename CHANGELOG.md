# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.12] - 2026-11-06

### Added
- `caddy_put_id`, `caddy_patch_id`, `caddy_post_id`, `caddy_post_config` and its alias `caddy_set_config` change the live proxy config, so they are destructive and take `confirm` like `caddy_load_config`. A stdio or no-auth caller passes `confirm=true`; without it the call is refused with a message to repeat it with `confirm=true`.

## [2.3.11] - 2026-11-06

### Added
- `caddy_load_config`, `caddy_put_config` and `caddy_patch_config` change the live proxy config, so they are destructive and take `confirm` like `caddy_stop_server`. A stdio or no-auth caller passes `confirm=true`; without it the call is refused with a message to repeat it with `confirm=true`.

## [2.3.10] - 2026-11-06

### Added
- `caddy_stop_server` takes `confirm` and is marked destructive: it stops the live edge proxy.
- Complete connector surface on `scion-sdk>=0.9.0`: task contracts, data locations, business roles, an operator prompt and two role prompts, and the `caddy-mcp-observability` skill.

### Removed
- The four action-routed tools (`caddy_mcp_config`, `caddy_mcp_pki`, `caddy_mcp_reverse_proxy`, `caddy_mcp_debug`); every operation is already its own typed tool.

## [2.3.9] - 2026-11-06

### Fixed
- Rebuild on `scion-sdk>=0.7.0` (already the floor on main): the 2.3.8 image shipped scion-sdk 0.6.4, whose destructive tools (`caddy_delete_id`, `caddy_delete_config`, `caddy_stop_server`) could only be confirmed by client elicitation and were cancelled when called through arbora. Destructive tools now accept `confirm=true`.

## [2.3.8] - 2026-10-30

### Changed
- Require `scion-sdk>=0.6.4,<0.7.0`; `uv.lock` relocked.

## [2.3.5] - 2026-10-24

### Changed
- Central connector migration: requires `agent-connector-sdk>=0.5.4`; server bootstrap, version, containers, ontology artifacts, security scaffold and pre-commit config are provided centrally.

## [Unreleased]
### Added
- Added the source-backed `caddy-mcp-development` skill with the connector
  runtime, auth/TLS, focused checks, and Pages publication contract.
- 100% Caddy Admin API parity: added the default observability endpoints — `get_metrics` (`/metrics`), `get_debug_vars` (`/debug/vars`), and `get_debug_pprof` (`/debug/pprof/<profile>`) — to the API client (CONCEPT:CADDY-001).
- New `caddy_mcp_debug` action-dispatch MCP tool routing to `get_metrics` / `get_debug_vars` / `get_debug_pprof`, keeping MCP↔API parity at 100% (CONCEPT:CADDY-002).

## [0.15.0] - 2026-05-25
### Added
- Initial dynamic facade API client implementation.
- FastMCP server entry points and modular tools.
- Rich documentation templates, including standardized environment configuration.
- Complete test suite validating startup and facade execution.
- Standardized MIT License.
