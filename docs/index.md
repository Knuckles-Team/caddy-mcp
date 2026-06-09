# caddy-mcp

Caddy reverse-proxy **API + MCP Server** for the agent-utilities ecosystem — a
typed, deterministic tool surface over the Caddy **Admin API** for configuration,
PKI, and reverse-proxy management.

!!! info "Official documentation"
    This site is the canonical reference for `caddy-mcp`, maintained alongside every
    release.

[![PyPI](https://img.shields.io/pypi/v/caddy-mcp)](https://pypi.org/project/caddy-mcp/)
![MCP Server](https://badge.mcpx.dev?type=server 'MCP Server')
[![License](https://img.shields.io/pypi/l/caddy-mcp)](https://github.com/Knuckles-Team/caddy-mcp/blob/main/LICENSE)
[![GitHub](https://img.shields.io/badge/source-GitHub-181717?logo=github)](https://github.com/Knuckles-Team/caddy-mcp)

## Overview

`caddy-mcp` wraps the **Caddy Admin API** (the live configuration endpoint Caddy
exposes on `:2019`) with typed, deterministic MCP tools and a Pydantic-AI agent. It
provides:

- **`Api`** — a `requests`-based REST facade over the Caddy Admin API, organized by
  capability (configuration traversal, `@id`-tagged objects, config adaptation, PKI,
  reverse-proxy upstreams).
- **MCP tools** — action-dispatch tools for `config`, `pki`, and `reverse_proxy`,
  surfaced to any MCP client or policy router.
- **An A2A agent server** — the `caddy-agent` console script exposes the same
  capability as a conversational Pydantic-AI agent.

## Explore the documentation

<div class="grid cards" markdown>

- :material-rocket-launch: **[Installation](installation.md)** — pip, source, extras, and the prebuilt Docker image.
- :material-server-network: **[Deployment](deployment.md)** — run the MCP and agent servers, Docker Compose, Caddy + Technitium.
- :material-console: **[Usage](usage.md)** — the MCP tools, the `Api` client, and the agent.
- :material-database-cog: **[Backing Platform](platform.md)** — deploy Caddy with Docker and connect the Admin API.
- :material-sitemap: **[Overview](overview.md)** — the integration architecture and tool surface.
- :material-tag-multiple: **[Concepts](concepts.md)** — the `CONCEPT:CADDY-*` registry.

</div>

## Quick start

```bash
pip install "caddy-mcp[mcp]"
caddy-mcp                        # stdio MCP server (default transport)
```

Point it at a running Caddy Admin API:

```bash
export CADDY_URL=http://localhost:2019
caddy-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

See **[Installation](installation.md)** and **[Deployment](deployment.md)** for the
full matrix (PyPI extras, Docker image, all transports, the agent server, reverse
proxy, DNS).
