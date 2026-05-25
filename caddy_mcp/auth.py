"""CONCEPT:CADDY-003 Identity credentials loader and session manager."""
import os

from agent_utilities.base_utilities import get_logger, to_boolean

from caddy_mcp.api_client import Api

logger = get_logger(__name__)


def get_client() -> Api:
    """Get authenticated client for caddy_mcp."""
    base_url = os.getenv("CADDY_URL") or os.getenv("CADDY_MCP_BASE_URL", "")
    token = os.getenv("CADDY_TOKEN", "")
    username = os.getenv("CADDY_MCP_USERNAME", "")
    password = os.getenv("CADDY_MCP_PASSWORD", "")
    verify = to_boolean(os.getenv("CADDY_MCP_SSL_VERIFY", "True"))

    if not base_url:
        # Default fallback for testing
        base_url = "http://localhost"

    return Api(
        base_url=base_url,
        token=token,
        username=username,
        password=password,
        verify=verify,
    )
