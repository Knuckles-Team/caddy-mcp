"""MCP tools for config operations."""

from fastmcp import Context, FastMCP
from fastmcp.dependencies import Depends
from pydantic import Field

from caddy_mcp.auth import get_client


def register_config_tools(mcp: FastMCP):
    """Register Caddy MCP config tools.
    CONCEPT:CADDY-001
    """

    @mcp.tool(tags={"config"})
    async def caddy_mcp_config(
        action: str = Field(
            description="Action to perform. Must be one of: 'get_config', 'set_config', 'delete_config', 'load_config', 'get_routes'"
        ),
        params_json: str = Field(
            default="{}", description="JSON string of parameters."
        ),
        client=Depends(get_client),
        ctx: Context | None = Field(default=None, description="MCP context"),
    ) -> dict:
        """Manage Caddy MCP config operations."""
        if ctx:
            await ctx.info("Executing config operations...")
        import json

        try:
            kwargs = json.loads(params_json)
        except Exception as e:
            return {"error": f"Invalid params_json: {e}"}

        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        if action == "get_config":
            return client.get_config(**kwargs)
        if action == "set_config":
            return client.set_config(**kwargs)
        if action == "delete_config":
            return client.delete_config(**kwargs)
        if action == "load_config":
            return client.load_config(**kwargs)
        if action == "get_routes":
            return client.get_routes(**kwargs)

        raise ValueError(f"Unknown action: {action}")
