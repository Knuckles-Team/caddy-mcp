---
name: caddy-mcp-development
skill_type: skill
description: >-
  Develop and verify caddy-mcp as a connector-owned package while preserving its
  SDK Connector wiring, Caddy Admin API authentication and TLS boundary, action
  tools, packaged content, and source-backed spec-delivery publication.
---

# Caddy MCP Development

Use this skill for changes to the `caddy-mcp` connector. The package owns Caddy
Admin API calls, MCP action mappings, connector content, and its packaged skills;
the SDK transport, shared Pages renderer, and Pipelines hooks remain external
boundaries.

## Repository map and runtime boundary

- `caddy_mcp/__init__.py` creates the SDK `Connector` with `Api`, `get_client`,
  and `caddy_mcp.mcp.mcp_config` as the tool module. It serves `stdio` and
  `streamable-http`; preserve this connector identity and transport declaration.
- `caddy_mcp/mcp/mcp_config.py` owns the action-routed tools for Caddy config,
  PKI, reverse-proxy upstreams, debug endpoints, and topology ingestion. The
  API methods they call live in `caddy_mcp/api/api_client_config.py` and inherit
  request behavior from `caddy_mcp/api/api_client_base.py`.
- `caddy_mcp/auth.py` reads `CADDY_URL` (falling back to
  `CADDY_MCP_BASE_URL`), bearer `CADDY_TOKEN`, optional
  `CADDY_MCP_USERNAME`/`CADDY_MCP_PASSWORD`, and the named
  `CADDY_TLS_PROFILE`/`CADDY_TLS_PROFILE_REF`. Preserve SDK setting lookup and
  TLS profile resolution; never embed credentials or disable verification.
- `caddy_mcp/ontology/`, `caddy_mcp/prompts/`, `caddy_mcp/connectors/`, and
  `caddy_mcp/skills/` are packaged connector content. `pyproject.toml` already
  includes each tree through `caddy_mcp` package data; inspect a built wheel when
  changing content.
- The only declared console script is `caddy-mcp = agent_connector_sdk.cli:serve`.
  Do not invent a second server or claim a `caddy-agent` entry point.

## Rapid delivery: the 5-minute contract

1. Read the owning `specs/` row, this repository's `AGENTS.md`, and the focused
   tests before editing.
2. Inspect the active SDK Connector, action map, API client, auth/TLS path, and
   package-data declaration before changing runtime or packaged content.
3. Prefer the smallest connector-owned change. Preserve action names and payload
   schemas, Caddy API paths, `CADDY_*` settings, TLS verification, ontology
   mappings, and the SDK Connector boundary unless the owning requirement changes.
4. Run the focused publication/runtime tests through the narrow test-slot wrapper;
   run the repository hooks normally without `--no-verify` or skipped gates.
5. When packaged content changes, advance the patch version and update `uv.lock`
   together; inspect the wheel for the skill and other declared resources.
6. Treat Pages as separate proof: after the exact main SHA has a successful Pages
   run, check `/spec-delivery/`, its `index.html`, and `snapshot.json` over HTTPS
   and record the snapshot revision.

## Focused development commands

From the repository root:

```bash
uv sync --locked

/var/tmp/arbora-delivery/scale/run-narrow-test-slot.sh \
  uv run --locked --extra test pytest -q \
    tests/test_publication_workflow.py \
    tests/test_init_dynamics.py \
    tests/test_mcp_server.py \
    tests/test_api_client.py \
    tests/test_sdk_centralization.py

uvx pre-commit run --all-files
uvx pre-commit run --all-files --hook-stage pre-push
```

These checks cover the shared Pages/release contract, lazy runtime imports,
action dispatch, API client behavior, and SDK centralization. Do not replace them
with a live Caddy call or a credential-bearing test.

## Pages and package publication

`.github/workflows/pages.yml` is the sole Pages caller. It invokes
`pages_pipeline.yml@main` with `content_source: docs`,
`spec_dashboard_enabled: true`, and `.github/spec-dashboard.json`; keep its
manual dispatch and docs/spec/config/workflow path filters. The package workflow
uses the shared `connector: true` and `render_connector: true` callers. Preserve
the existing runtime, auth, and container environment contract while inspecting
generated output before making publication claims.

After a merge, verify the exact main SHA in the successful Pages run and probe:

```bash
curl -fsSI https://knuckles-team.github.io/caddy-mcp/
curl -fsSI https://knuckles-team.github.io/caddy-mcp/spec-delivery/
curl -fsSI https://knuckles-team.github.io/caddy-mcp/spec-delivery/index.html
curl -fsS https://knuckles-team.github.io/caddy-mcp/spec-delivery/snapshot.json
```

Do not claim a Pages or package result from local source inspection alone. Keep
generated status changes with the Pipelines/status owner.

## Change discipline

- Keep Caddy API calls, MCP schemas, auth settings, ontology mappings, and
  ingestion declarations under the connector's existing boundary. SDK and shared
  renderer behavior belong to their owner repositories.
- Use injected `CADDY_*` configuration only; never print or commit token/password
  values, host-specific profiles, or generated runtime state.
- Preserve the Caddy Admin API's request/auth/TLS semantics and the existing
  action-to-method mappings. For mutations, inspect current state and verify the
  durable result through the governed procedure.
- Generated status files and central promotion are owned by Pipelines; this skill
  does not authorize editing `specs/*/status.json`.
