# Deployment

This page covers running `caddy-mcp` as a long-lived server: the transports, a Docker
Compose stack, the optional A2A agent server, putting it behind a Caddy reverse proxy,
and giving it a DNS name with Technitium. To provision the **Caddy server** it
connects to, see [Backing Platform](platform.md).

> `caddy-mcp` ships **two** console scripts: `caddy-mcp` (the MCP tool surface) and
> `caddy-agent` (a Pydantic-AI A2A agent that consumes those tools). Deploy the MCP
> server on its own for tool access, or pair it with the agent server for a
> conversational interface.

## Run the MCP server

The transport is selected with `--transport` (or the `TRANSPORT` env var):

=== "stdio (default)"

    ```bash
    caddy-mcp
    ```
    For IDE / desktop MCP clients that launch the server as a subprocess.

=== "streamable-http"

    ```bash
    caddy-mcp --transport streamable-http --host 0.0.0.0 --port 8000
    ```
    A network server with a `/health` endpoint and `/mcp` route.

=== "sse"

    ```bash
    caddy-mcp --transport sse --host 0.0.0.0 --port 8000
    ```

Health check (HTTP transports):

```bash
curl -s http://localhost:8000/health        # {"status":"OK"}
```

## Configuration (environment)

`caddy-mcp` is configured entirely from the environment. The **required** set:

| Var | Default | Meaning |
|---|---|---|
| `CADDY_URL` | `http://localhost:2019` | Caddy Admin API URL endpoint |
| `CADDY_TOKEN` | _(unset)_ | Optional bearer token if the Admin API is secured |

Plus `HOST` / `PORT` / `TRANSPORT` for HTTP transports, and `CONFIGTOOL` (default
`True`) to register the configuration tool set. A template is provided in
[`.env.example`](https://github.com/Knuckles-Team/caddy-mcp/blob/main/.env.example) —
copy it to `.env` and fill in your values.

## Docker Compose

The repo ships [`docker/mcp.compose.yml`](https://github.com/Knuckles-Team/caddy-mcp/blob/main/docker/mcp.compose.yml).
It reads a sibling `.env` and publishes the HTTP server on `:8000`:

```yaml
services:
  caddy-mcp:
    image: knucklessg1/caddy-mcp:latest
    container_name: caddy-mcp
    hostname: caddy-mcp
    restart: always
    env_file:
      - .env
    environment:
      - PYTHONUNBUFFERED=1
      - HOST=0.0.0.0
      - PORT=8000
      - TRANSPORT=streamable-http
      - CADDY_URL
      - CADDY_TOKEN
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "python3", "-c", "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
```

```bash
cp .env.example .env          # then edit CADDY_URL / CADDY_TOKEN
docker compose -f docker/mcp.compose.yml up -d
docker compose -f docker/mcp.compose.yml logs -f
```

## Agent server

`caddy-mcp` also ships an **A2A agent server** via the `caddy-agent` console script.
The agent connects to a running MCP server (its tool source) and exposes a
conversational Pydantic-AI interface over HTTP.

```bash
# Start the agent; point it at the MCP server's HTTP endpoint
caddy-agent --mcp-url http://caddy-mcp:8000/mcp --host 0.0.0.0 --port 9000
```

The agent reads its tool registration from `mcp_config.json` (bundled in the package)
or from the `--mcp-url` of a remote MCP server. Provide a model provider with
`--provider` / `--model-id` (or the corresponding environment variables). A Compose
service for the agent mirrors the MCP service, wiring `MCP_URL` at its own published
port (for example `:9000`):

```yaml
# docker/agent.compose.yml
services:
  caddy-agent:
    image: knucklessg1/caddy-mcp:latest
    container_name: caddy-agent
    hostname: caddy-agent
    restart: always
    entrypoint: ["caddy-agent"]
    env_file:
      - .env
    environment:
      - PYTHONUNBUFFERED=1
      - MCP_URL=http://caddy-mcp:8000/mcp
      - HOST=0.0.0.0
      - PORT=9000
    ports:
      - "9000:9000"
    depends_on:
      - caddy-mcp
```

## Behind a Caddy reverse proxy

Expose the HTTP server on a hostname with automatic TLS. Add to your `Caddyfile`:

```caddy
# Internal (self-signed) — homelab .arpa zone
caddy-mcp.arpa {
    tls internal
    reverse_proxy caddy-mcp:8000
}
```

```caddy
# Public — automatic Let's Encrypt
caddy-mcp.example.com {
    reverse_proxy caddy-mcp:8000
}
```

Reload Caddy:

```bash
docker compose -f services/caddy/compose.yml exec caddy caddy reload --config /etc/caddy/Caddyfile
```

## DNS with Technitium

Point the hostname at the host running Caddy. Via the Technitium API:

```bash
curl -s "http://technitium.arpa:5380/api/zones/records/add" \
  --data-urlencode "token=$TECHNITIUM_DNS_TOKEN" \
  --data-urlencode "domain=caddy-mcp.arpa" \
  --data-urlencode "zone=arpa" \
  --data-urlencode "type=A" \
  --data-urlencode "ipAddress=10.0.0.10" \
  --data-urlencode "ttl=3600"
```

…or add an **A record** `caddy-mcp.arpa → <caddy-host-ip>` in the Technitium web
console (`http://technitium.arpa:5380`). The ecosystem
[`technitium-dns-mcp`](https://knuckles-team.github.io/technitium-dns-mcp/) automates
this as a tool.

## Register with an MCP client

Add to your client's `mcp_config.json` (multiplexer nickname `cd`):

```json
{
  "mcpServers": {
    "caddy-mcp": {
      "command": "uv",
      "args": ["run", "caddy-mcp"],
      "env": {
        "CADDY_URL": "http://your-caddy:2019",
        "CADDY_TOKEN": ""
      }
    }
  }
}
```

For a remote HTTP server, point the client at `http://caddy-mcp.arpa/mcp` instead.
