# Installation

`caddy-mcp` is a standard Python package and a prebuilt container image. Choose the
path that matches how you want to run it.

## Requirements

- **Python 3.11 – 3.14**.
- A reachable **Caddy Admin API** (Caddy listens on `:2019` by default) — see
  [Backing Platform](platform.md) to deploy one locally.

## From PyPI (recommended)

```bash
pip install caddy-mcp
```

### Optional extras

The base install is intentionally minimal. Install the extra for what you need:

| Extra | Install | Pulls in |
|---|---|---|
| `mcp` | `pip install "caddy-mcp[mcp]"` | FastMCP MCP-server runtime (`agent-utilities[mcp]`) |
| `agent` | `pip install "caddy-mcp[agent]"` | Pydantic-AI agent + Logfire tracing (`agent-utilities[agent,logfire]`) |
| `all` | `pip install "caddy-mcp[all]"` | Everything above |
| `test` | `pip install "caddy-mcp[test]"` | `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-xdist` |

```bash
# Typical: run the MCP server and the A2A agent
pip install "caddy-mcp[all]"
```

## From source

```bash
git clone https://github.com/Knuckles-Team/caddy-mcp.git
cd caddy-mcp
pip install -e ".[all]"          # editable install with every extra
```

With [`uv`](https://docs.astral.sh/uv/):

```bash
uv pip install -e ".[all]"
uv run caddy-mcp
```

## Prebuilt Docker image

A multi-stage, slim image is published on every release (installs `caddy-mcp[all]`,
entrypoint `caddy-mcp`):

```bash
docker pull knucklessg1/caddy-mcp:latest

docker run --rm -i \
  -e CADDY_URL=http://your-caddy:2019 \
  knucklessg1/caddy-mcp:latest        # stdio transport (default)
```

For an HTTP server with a published port, see [Deployment](deployment.md).

## Verify the install

```bash
caddy-mcp --help
python -c "import caddy_mcp; print(caddy_mcp.__version__)"
```

## Next steps

- **[Deployment](deployment.md)** — run it as a long-lived MCP and agent server behind Caddy + DNS.
- **[Usage](usage.md)** — call the tools, the `Api` client, and the agent.
- **[Configuration](deployment.md#configuration-environment)** — every environment variable.
