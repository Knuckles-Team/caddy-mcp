# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- 100% Caddy Admin API parity: added the default observability endpoints — `get_metrics` (`/metrics`), `get_debug_vars` (`/debug/vars`), and `get_debug_pprof` (`/debug/pprof/<profile>`) — to the API client (CONCEPT:CADDY-001).
- New `caddy_mcp_debug` action-dispatch MCP tool routing to `get_metrics` / `get_debug_vars` / `get_debug_pprof`, keeping MCP↔API parity at 100% (CONCEPT:CADDY-002).

## [0.15.0] - 2026-05-25
### Added
- Initial dynamic facade API client implementation.
- FastMCP server entry points and modular tools.
- Rich documentation templates, including standardized environment configuration.
- Comprehensive test suite validating startup and facade execution.
- Standardized MIT License.
