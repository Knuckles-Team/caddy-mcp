---
name: caddy-mcp-operations
skill_type: skill
description: >-
  Read and change the live Caddy configuration through caddy-mcp: inspect routes, add, change and remove routes by @id or config path, validate a Caddyfile, reload the whole config, and stop the proxy. Use when a service needs a route published, moved or retired on the edge proxy.
---

# Caddy operations

Caddy applies every change atomically to live traffic. Work in small scoped edits.

## Inspect

1. `caddy_get_routes` lists the HTTP servers and routes. `caddy_get_config` with `path` reads any node (for example `apps/http/servers`). `caddy_get_id` reads a node by its `@id`.

## Add a route

1. `caddy_get_config` on the target path to see the current array.
2. If the input is a Caddyfile, `caddy_adapt_config` (`config`, `config_adapter=caddyfile`) and read the JSON it returns.
3. `caddy_post_config` appends to an array or sets an object at `path`. `caddy_post_id` does the same under an `@id`. `caddy_set_config` is an alias of `caddy_post_config`.
4. `caddy_get_routes` to confirm the route is live.

## Change a route

1. `caddy_get_id` to read the node.
2. `caddy_put_id` creates or replaces by `@id`, `caddy_patch_id` merges into an existing node. `caddy_put_config` and `caddy_patch_config` do the same by `path`.
3. Pass `if_match` (the ETag from the read) to guard against a concurrent edit.
4. `caddy_get_routes` to verify.

## Remove a route

1. `caddy_get_id` (or `caddy_get_config`) to confirm the target.
2. `caddy_delete_id` or `caddy_delete_config` with `confirm=true` after the requester agrees.
3. `caddy_get_routes` to verify it is gone.

## Replace the whole configuration

Rare. `caddy_adapt_config` to validate, `caddy_get_config` to keep a copy, then `caddy_load_config` (`force_reload` only when asked). Check `caddy_get_routes` afterwards.

## Stop the proxy

`caddy_stop_server` shuts the Caddy process down and takes ingress offline. It needs `confirm=true`. Read `caddy_get_routes` first so the requester sees what goes dark.

## Rules

- Never print a private key or secret from a config read.
- Cite the `@id` or path you changed.
- A delete, a stop or a whole-config load needs the requester's explicit yes.
