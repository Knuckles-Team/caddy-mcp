# Usage — API / Agent / MCP

`caddy-mcp` exposes the same capability three ways: as **MCP tools** an agent calls,
as a **Python API** (`Api`) the operator import, and as a **Pydantic-AI agent**. The complete
tool surface is summarized in [Overview](overview.md).

## As an MCP server

Once [deployed](deployment.md), the server serves one typed tool per Caddy Admin API
operation (`caddy_<operation>`):

| Area | Tools |
|---|---|
| Configuration | `caddy_get_config`, `caddy_post_config`, `caddy_set_config`, `caddy_put_config`, `caddy_patch_config`, `caddy_delete_config`, `caddy_load_config`, `caddy_adapt_config`, `caddy_get_routes` |
| Nodes by `@id` | `caddy_get_id`, `caddy_post_id`, `caddy_put_id`, `caddy_patch_id`, `caddy_delete_id` |
| Server control | `caddy_stop_server` |
| PKI | `caddy_get_pki_ca`, `caddy_get_pki_ca_certificates` |
| Reverse proxy | `caddy_get_reverse_proxy_upstreams` |
| Observability | `caddy_get_metrics`, `caddy_get_debug_vars`, `caddy_get_debug_pprof` |
| Knowledge graph | `caddy_ingest_topology` |

Together these cover the full Caddy Admin API surface: configuration (`/load`, `/stop`,
`/config/...`, `/id/...`, `/adapt`), PKI (`/pki/ca/...`), reverse-proxy upstream health
(`/reverse_proxy/upstreams`), and the observability endpoints served on the admin
endpoint by default (`/metrics`, `/debug/vars`, `/debug/pprof/...`).

`caddy_delete_config`, `caddy_delete_id` and `caddy_stop_server` are destructive. Each
takes `confirm=true` when the client cannot answer a confirmation prompt.
`caddy_stop_server` stops the live edge proxy.

Example agent prompts that map onto these tools:

- *"Export Caddy's current configuration"* -> `caddy_get_config`
- *"Show the reverse-proxy upstream health"* -> `caddy_get_reverse_proxy_upstreams`
- *"Return the local PKI CA certificate chain"* -> `caddy_get_pki_ca_certificates`
- *"Scrape Caddy's Prometheus metrics"* -> `caddy_get_metrics`
- *"Grab a heap profile in text form"* -> `caddy_get_debug_pprof` with `profile="heap"` and `params={"debug": 1}`

## As a Python API

`Api` (`caddy_mcp.api_client`) is a `requests`-based facade over the Caddy Admin API.
Build one directly, or from the environment with `get_client()`.

```python
from caddy_mcp.api_client import Api

api = Api(
    base_url="https://caddy.example.invalid",
    token="",                 # optional bearer token
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
