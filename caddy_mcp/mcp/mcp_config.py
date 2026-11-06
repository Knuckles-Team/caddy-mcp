"""MCP tools for Caddy operations."""

from typing import Any

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from caddy_mcp.auth import get_client


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
        """Natively ingest the live Caddy topology into medulla as typed nodes.

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
            await ingest_upstreams(upstreams) if upstreams else {"nodes": 0, "edges": 0}
        )
        srv_result = (
            await ingest_servers(servers) if servers else {"nodes": 0, "edges": 0}
        )
        return {
            "upstreams_listed": len(upstreams),
            "servers_listed": len(servers),
            "ingested": {"upstreams": up_result, "servers": srv_result},
        }
