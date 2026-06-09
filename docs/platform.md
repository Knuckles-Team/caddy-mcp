# Backing Platform — Caddy

`caddy-mcp` is a **client** of a Caddy server's **Admin API** (the live configuration
endpoint Caddy exposes on `:2019`). This page provides a Docker recipe for deploying
Caddy locally to serve as the target of `CADDY_URL`. For production topologies, follow
the upstream [Caddy documentation](https://caddyserver.com/docs/).

!!! note "Backing-system recipe"
    Each connector in the ecosystem follows the same convention — a
    `docs/platform.md` recipe for the system it integrates with, accompanied by a
    sample Compose stack that mirrors [`services/`](https://github.com/Knuckles-Team).
    Systems offered only as a managed service have no local recipe.

## Single-node deployment (Compose)

Caddy publishes the official `caddy` image. The following stack runs one Caddy server
and **exposes the Admin API** on `:2019` so `caddy-mcp` can manage it. By default the
Admin API binds to `localhost`; the `admin 0.0.0.0:2019` global directive makes it
reachable from the MCP container.

```yaml
# docker/caddy.compose.yml
services:
  caddy:
    image: docker.io/library/caddy:latest
    container_name: caddy
    hostname: caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "2019:2019"            # Admin API (managed by caddy-mcp)
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config

volumes:
  caddy_data:
  caddy_config:
```

A minimal `Caddyfile` that opens the Admin API to the Docker network:

```caddy
{
    admin 0.0.0.0:2019
}

:80 {
    respond "Caddy is running"
}
```

```bash
docker compose -f docker/caddy.compose.yml up -d

# Confirm the Admin API answers
curl -s http://localhost:2019/config/
```

## Connect caddy-mcp

```bash
export CADDY_URL=http://localhost:2019
export CADDY_TOKEN=                       # set only if the Admin API is secured

caddy-mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

## Combined deployment

A combined stack places Caddy and the MCP server on one Docker network, so the server
reaches the Admin API by container name:

```yaml
# docker/stack.compose.yml
services:
  caddy:
    image: docker.io/library/caddy:latest
    hostname: caddy
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config

  caddy-mcp:
    image: knucklessg1/caddy-mcp:latest
    depends_on: [caddy]
    environment:
      - CADDY_URL=http://caddy:2019
      - TRANSPORT=streamable-http
      - HOST=0.0.0.0
      - PORT=8000
    ports: ["8000:8000"]

volumes:
  caddy_data:
  caddy_config:
```

```bash
docker compose -f docker/stack.compose.yml up -d
```

With Caddy running and reachable, the [MCP tools](usage.md#as-an-mcp-server) and the
[`Api` client](usage.md#as-a-python-api) manage its configuration, PKI, and
reverse-proxy upstreams over the Admin API.
