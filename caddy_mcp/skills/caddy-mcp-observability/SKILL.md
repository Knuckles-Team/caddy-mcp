---
name: caddy-mcp-observability
skill_type: skill
description: >-
  Check Caddy edge health through caddy-mcp: upstream health, PKI authorities and certificates, Prometheus metrics, expvar and pprof, and topology ingestion into the knowledge graph. Use for health reviews, certificate checks and graph refreshes. Read-only.
---

# Caddy observability

All tools here are read-only except the graph ingest, which writes knowledge-graph nodes only.

## Upstream health

`caddy_get_reverse_proxy_upstreams` returns each upstream `address`, `num_requests` and `fails`. Report any upstream with failures and the routes that dial it (`caddy_get_routes`).

## PKI

`caddy_get_pki_ca` (`ca_id`, for example `local`) returns the authority. `caddy_get_pki_ca_certificates` returns the certificates it issued. Report expiry dates.

## Diagnostics

`caddy_get_metrics` returns Prometheus text. `caddy_get_debug_vars` returns expvar. `caddy_get_debug_pprof` (`profile`, `params`) returns a Go profile. Use these only when asked to dig into load or memory.

## Topology

`caddy_ingest_topology` reads upstreams and routes and writes `ReverseProxy`, `Route` and `Upstream` nodes to the knowledge graph. Run it after route changes.
