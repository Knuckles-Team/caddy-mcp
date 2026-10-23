# CONN-CADDY-MCP-CONNECTOR-CONTENT — Design and implementation plan

Governing spec: [spec.md](spec.md).

## Architecture

`pyproject.toml` declares `caddy-mcp` as the connector identity. `create_mcp_server` resolves the packaged content of `caddy_mcp` from it.
