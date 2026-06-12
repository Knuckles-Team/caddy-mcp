# Usage — API / Agent / MCP

`caddy-mcp` exposes the same capability three ways: as **MCP tools** an agent calls,
as a **Python API** (`Api`) you import, and as a **Pydantic-AI agent**. The complete
tool surface is summarized in [Overview](overview.md).

## As an MCP server

Once [deployed](deployment.md), the server registers action-dispatch tools grouped by
Caddy Admin API capability:

| Tool | Tag | Actions |
|---|---|---|
| `caddy_mcp_config` | `config` | `get_config`, `post_config`, `set_config`, `put_config`, `patch_config`, `delete_config`, `load_config`, `stop_server`, `get_id`, `post_id`, `put_id`, `patch_id`, `delete_id`, `adapt_config`, `get_routes` |
| `caddy_mcp_pki` | `pki` | `get_pki_ca`, `get_pki_ca_certificates` |
| `caddy_mcp_reverse_proxy` | `reverse_proxy` | `get_reverse_proxy_upstreams` |
| `caddy_mcp_debug` | `debug` | `get_metrics`, `get_debug_vars`, `get_debug_pprof` |

Together these cover the full Caddy Admin API surface: configuration (`/load`, `/stop`,
`/config/…`, `/id/…`, `/adapt`), PKI (`/pki/ca/…`), reverse-proxy upstream health
(`/reverse_proxy/upstreams`), and the observability endpoints served on the admin
endpoint by default (`/metrics`, `/debug/vars`, `/debug/pprof/…`).

Each tool takes an `action` and a `params_json` string matching the underlying method
signature. Example agent prompts that map onto these tools:

- *"Export Caddy's current configuration"* → `caddy_mcp_config` with `get_config`
- *"Show the reverse-proxy upstream health"* → `caddy_mcp_reverse_proxy` with `get_reverse_proxy_upstreams`
- *"Return the local PKI CA certificate chain"* → `caddy_mcp_pki` with `get_pki_ca_certificates`
- *"Scrape Caddy's Prometheus metrics"* → `caddy_mcp_debug` with `get_metrics`
- *"Grab a heap profile in text form"* → `caddy_mcp_debug` with `get_debug_pprof` and `params_json='{"profile": "heap", "params": {"debug": 1}}'`

## As a Python API

`Api` (`caddy_mcp.api_client`) is a `requests`-based facade over the Caddy Admin API.
Build one directly, or from the environment with `get_client()`.

```python
from caddy_mcp.api_client import Api

api = Api(
    base_url="http://localhost:2019",
    token="",                 # optional bearer token
    verify=True,
)

# Reads
config = api.get_config()                       # full live configuration
routes = api.get_routes()                       # http servers / routes
upstreams = api.get_reverse_proxy_upstreams()   # upstream health
ca = api.get_pki_ca("local")                    # PKI app CA info

# Observability (served on the admin endpoint by default)
metrics = api.get_metrics()                      # Prometheus exposition text
expvars = api.get_debug_vars()                   # Go expvar JSON
heap = api.get_debug_pprof("heap", params={"debug": 1})  # pprof profile
```

Build a client straight from the environment:

```python
from caddy_mcp.auth import get_client
api = get_client()        # reads CADDY_URL / CADDY_TOKEN from the environment / .env
```

### Writes

Mutating calls drive the live Caddy configuration. The facade supports the full Admin
API surface — load, set, patch, and delete by config path or `@id` tag:

```python
# Load a complete configuration (JSON or a Caddyfile)
api.load_config(caddyfile_text, config_adapter="caddyfile")

# Set or replace an object at a named config path
api.set_config("apps/http/servers/srv0/routes", route_definition)

# Patch / delete by @id tag
api.patch_id("my_proxy/upstreams", upstreams)
api.delete_config("apps/http/servers/srv0/routes/0")

# Adapt a Caddyfile to Caddy JSON without loading it
api.adapt_config(caddyfile_text, config_adapter="caddyfile")
```

## As an agent

The `caddy-agent` console script starts a Pydantic-AI A2A agent that consumes the MCP
tools and exposes a conversational interface. Point it at a running MCP server:

```bash
caddy-agent --mcp-url http://caddy-mcp:8000/mcp --host 0.0.0.0 --port 9000
```

Provide a model provider and identity with `--provider` / `--model-id` (or the
corresponding environment variables). See [Deployment](deployment.md#agent-server) for
the Compose service and `MCP_URL` wiring.
