"""MCP tools for Caddy operations."""

from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from caddy_mcp.auth import get_client

# Dispatch table for caddy_mcp_config: action name -> client method name.
# A few actions (e.g. "set_config") are documented aliases of another
# client method rather than a 1:1 name match.
_CONFIG_ACTION_METHODS = {
    "get_config": "get_config",
    "post_config": "post_config",
    "set_config": "post_config",
    "put_config": "put_config",
    "patch_config": "patch_config",
    "delete_config": "delete_config",
    "load_config": "load_config",
    "stop_server": "stop_server",
    "get_id": "get_id",
    "post_id": "post_id",
    "put_id": "put_id",
    "patch_id": "patch_id",
    "delete_id": "delete_id",
    "adapt_config": "adapt_config",
    "get_routes": "get_routes",
}


def _parsed_action_kwargs(params_json: str) -> dict[str, Any] | None:
    """Parse ``params_json`` into a kwargs dict, dropping ``None`` values.

    Returns ``None`` if ``params_json`` is not valid JSON.
    """
    import json

    try:
        kwargs = json.loads(params_json)
    except Exception:
        return None
    return {k: v for k, v in kwargs.items() if v is not None}


def _dispatch_config_action(client: Any, action: str, kwargs: dict[str, Any]) -> Any:
    method_name = _CONFIG_ACTION_METHODS.get(action)
    if method_name is None:
        raise ValueError(f"Unknown config action: {action}")
    return getattr(client, method_name)(**kwargs)


def register_config_tools(mcp: FastMCP):
    """Register Caddy MCP config, PKI, and reverse proxy tools.
    CONCEPT:CD-OS.config.caddy
    """

    @mcp.tool(tags={"config"})
    async def caddy_mcp_config(
        action: str = Field(
            description=(
                "Action to perform. Must be one of: "
                "'get_config', 'post_config', 'set_config', 'put_config', 'patch_config', "
                "'delete_config', 'load_config', 'stop_server', 'get_id', 'post_id', "
                "'put_id', 'patch_id', 'delete_id', 'adapt_config', 'get_routes'"
            )
        ),
        params_json: str = Field(
            default="{}",
            description="JSON string of parameters matching the method signature.",
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Manage Caddy configuration and server control."""
        if ctx:
            await ctx.info(f"Executing config operation '{action}'...")
        kwargs = _parsed_action_kwargs(params_json)
        if kwargs is None:
            return {"error": "Operation failed"}
        return _dispatch_config_action(client, action, kwargs)

    @mcp.tool(tags={"pki"})
    async def caddy_mcp_pki(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_pki_ca', 'get_pki_ca_certificates'"
        ),
        params_json: str = Field(
            default="{}",
            description="JSON string of parameters matching the method signature.",
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Manage Caddy PKI app CAs and certificates."""
        if ctx:
            await ctx.info(f"Executing PKI operation '{action}'...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception:
            return {"error": "Operation failed"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_pki_ca":
            return client.get_pki_ca(**kwargs)
        if action == "get_pki_ca_certificates":
            return client.get_pki_ca_certificates(**kwargs)

        raise ValueError(f"Unknown PKI action: {action}")

    @mcp.tool(tags={"reverse_proxy"})
    async def caddy_mcp_reverse_proxy(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_reverse_proxy_upstreams'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Query Caddy reverse proxy upstream health and status."""
        if ctx:
            await ctx.info(f"Executing reverse proxy operation '{action}'...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception:
            return {"error": "Operation failed"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_reverse_proxy_upstreams":
            return client.get_reverse_proxy_upstreams(**kwargs)

        raise ValueError(f"Unknown reverse proxy action: {action}")

    @mcp.tool(tags={"debug"})
    async def caddy_mcp_debug(
        action: str = Field(
            description=(
                "Action to perform. Must be one of: "
                "'get_metrics' (Prometheus exposition), 'get_debug_vars' (expvar), "
                "'get_debug_pprof' (Go pprof profile; params: profile, params)"
            )
        ),
        params_json: str = Field(
            default="{}",
            description="JSON string of parameters matching the method signature.",
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Inspect Caddy observability and profiling endpoints (metrics, expvar, pprof)."""
        if ctx:
            await ctx.info(f"Executing debug operation '{action}'...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception:
            return {"error": "Operation failed"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_metrics":
            return client.get_metrics(**kwargs)
        if action == "get_debug_vars":
            return client.get_debug_vars(**kwargs)
        if action == "get_debug_pprof":
            return client.get_debug_pprof(**kwargs)

        raise ValueError(f"Unknown debug action: {action}")


async def _fetched_upstreams(client: Any, ctx: Context | None) -> list[Any]:
    """Best-effort fetch of reverse-proxy upstream health; ``[]`` on failure."""
    try:
        resp = client.get_reverse_proxy_upstreams()
        return resp if isinstance(resp, list) else (resp or [])
    except Exception as e:  # noqa: BLE001 — best-effort
        if ctx:
            await ctx.info(f"upstreams unavailable: {type(e).__name__}")
        return []


async def _fetched_servers(client: Any, ctx: Context | None) -> dict[str, Any]:
    """Best-effort fetch of the ``apps/http/servers`` config; ``{}`` on failure."""
    try:
        resp = client.get_routes()
        return resp if isinstance(resp, dict) else {}
    except Exception as e:  # noqa: BLE001 — best-effort
        if ctx:
            await ctx.info(f"routes unavailable: {type(e).__name__}")
        return {}


def register_kg_ingest_tools(mcp: FastMCP):
    """Register the native knowledge-graph ingestion tool for Caddy topology.
    CONCEPT:AU-KG.ingest.enterprise-source-extractor
    """

    @mcp.tool(tags={"kg"})
    async def caddy_ingest_topology(
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """Natively ingest the live Caddy topology into epistemic-graph as typed nodes.

        Reads the reverse-proxy upstreams (``get_reverse_proxy_upstreams``) and the HTTP
        servers/routes config (``get_routes``) via the real client, then pushes them into
        the knowledge graph as ``:ReverseProxy`` / ``:Route`` / ``:Upstream`` nodes with
        ``:hasRoute`` / ``:routesToUpstream`` / ``:proxiesTo`` links through native
        ingestion. Engine, validation, and transaction failures propagate.
        CONCEPT:AU-KG.ingest.enterprise-source-extractor.
        """
        if ctx:
            await ctx.info("Ingesting Caddy topology into the knowledge graph...")

        from caddy_mcp.kg_ingest import ingest_servers, ingest_upstreams

        upstreams = await _fetched_upstreams(client, ctx)
        servers = await _fetched_servers(client, ctx)

        up_result = (
            ingest_upstreams(upstreams) if upstreams else {"nodes": 0, "edges": 0}
        )
        srv_result = ingest_servers(servers) if servers else {"nodes": 0, "edges": 0}
        return {
            "upstreams_listed": len(upstreams),
            "servers_listed": len(servers),
            "ingested": {"upstreams": up_result, "servers": srv_result},
        }

    @mcp.tool(tags={"kg", "security"})
    async def caddy_ingest_crowdsec_decisions(
        params_json: str = Field(
            default="{}",
            description="JSON with optional 'startup' (bool: full decision set, default true).",
        ),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> Any:
        """EH-410: ingest the edge CrowdSec decisions (bouncer stream of the Local
        API at CROWDSEC_LAPI_URL, key from CROWDSEC_BOUNCER_KEY_REF in OpenBao) as
        ``:IntrusionDecision`` nodes; ban targets kept whole, deleted decisions
        marked inactive."""
        import json as _json

        from agent_utilities.core.config import setting
        from agent_utilities.security.secrets_client import create_secrets_client

        from caddy_mcp.crowdsec_feed import fetch_decisions, ingest_decisions

        try:
            kwargs = _json.loads(params_json) if params_json else {}
        except ValueError:
            return {"error": "params_json is not valid JSON"}
        url = str(setting("CROWDSEC_LAPI_URL", "") or "")
        ref = str(setting("CROWDSEC_BOUNCER_KEY_REF", "") or "")
        key = create_secrets_client().resolve_ref(ref) if ref else ""
        if not url or not key:
            return {
                "error": "CROWDSEC_LAPI_URL / CROWDSEC_BOUNCER_KEY_REF not configured"
            }
        if ctx:
            await ctx.info("Ingesting CrowdSec decisions into the knowledge graph...")
        stream = fetch_decisions(
            url, str(key), startup=bool(kwargs.get("startup", True))
        )
        result = ingest_decisions(stream["new"], stream["deleted"])
        return {
            "new": len(stream["new"]),
            "deleted": len(stream["deleted"]),
            "ingested": result,
        }
