# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.5] - 2026-10-24

### Changed
- Central connector migration: requires `agent-connector-sdk>=0.5.4`; server bootstrap, version, containers, ontology artifacts, security scaffold and pre-commit config are provided centrally.

## [Unreleased]
### Added
- 100% Caddy Admin API parity: added the default observability endpoints — `get_metrics` (`/metrics`), `get_debug_vars` (`/debug/vars`), and `get_debug_pprof` (`/debug/pprof/<profile>`) — to the API client (CONCEPT:CADDY-001).
- New `caddy_mcp_debug` action-dispatch MCP tool routing to `get_metrics` / `get_debug_vars` / `get_debug_pprof`, keeping MCP↔API parity at 100% (CONCEPT:CADDY-002).

## [0.15.0] - 2026-05-25
### Added
- Initial dynamic facade API client implementation.
- FastMCP server entry points and modular tools.
- Rich documentation templates, including standardized environment configuration.
- Complete test suite validating startup and facade execution.
- Standardized MIT License.
