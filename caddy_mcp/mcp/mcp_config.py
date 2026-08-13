"""MCP tools for Caddy operations."""

from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from caddy_mcp.auth import get_client


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
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception:
            return {"error": "Operation failed"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # Route matching action
        if action == "get_config":
            return client.get_config(**kwargs)
        if action in ("post_config", "set_config"):
            return client.post_config(**kwargs)
        if action == "put_config":
            return client.put_config(**kwargs)
        if action == "patch_config":
            return client.patch_config(**kwargs)
        if action == "delete_config":
            return client.delete_config(**kwargs)
        if action == "load_config":
            return client.load_config(**kwargs)
        if action == "stop_server":
            return client.stop_server(**kwargs)
        if action == "get_id":
            return client.get_id(**kwargs)
        if action == "post_id":
            return client.post_id(**kwargs)
        if action == "put_id":
            return client.put_id(**kwargs)
        if action == "patch_id":
            return client.patch_id(**kwargs)
        if action == "delete_id":
            return client.delete_id(**kwargs)
        if action == "adapt_config":
            return client.adapt_config(**kwargs)
        if action == "get_routes":
            return client.get_routes(**kwargs)

        raise ValueError(f"Unknown config action: {action}")

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

        upstreams: list[Any] = []
        try:
            resp = client.get_reverse_proxy_upstreams()
            upstreams = resp if isinstance(resp, list) else (resp or [])
        except Exception as e:  # noqa: BLE001 — best-effort
            if ctx:
                await ctx.info(f"upstreams unavailable: {type(e).__name__}")

        servers: dict[str, Any] = {}
        try:
            resp = client.get_routes()
            if isinstance(resp, dict):
                servers = resp
        except Exception as e:  # noqa: BLE001 — best-effort
            if ctx:
                await ctx.info(f"routes unavailable: {type(e).__name__}")

        up_result = (
            ingest_upstreams(upstreams) if upstreams else {"nodes": 0, "edges": 0}
        )
        srv_result = ingest_servers(servers) if servers else {"nodes": 0, "edges": 0}
        return {
            "upstreams_listed": len(upstreams),
            "servers_listed": len(servers),
            "ingested": {"upstreams": up_result, "servers": srv_result},
        }
