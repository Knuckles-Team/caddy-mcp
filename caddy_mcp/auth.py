"""CONCEPT:CD-OS.identity.caddy Identity credentials loader and session manager."""

from agent_utilities.base_utilities import get_logger
from agent_utilities.core.config import setting
from agent_utilities.core.transport_security import resolve_configured_tls_profile

from caddy_mcp.api_client import Api

logger = get_logger(__name__)


def get_client() -> Api:
    """Get authenticated client for caddy_mcp."""
    base_url = setting("CADDY_URL") or setting("CADDY_MCP_BASE_URL", "")
    token = setting("CADDY_TOKEN", "")
    username = setting("CADDY_MCP_USERNAME", "")
    password = setting("CADDY_MCP_PASSWORD", "")
    tls_profile = resolve_configured_tls_profile(
        "caddy",
        profile_name=setting("CADDY_TLS_PROFILE", None),
        profile_ref=setting("CADDY_TLS_PROFILE_REF", None),
    )

    if not base_url:
        # Default fallback for testing
        base_url = "http://localhost"

    return Api(
        base_url=base_url,
        token=token,
        username=username,
        password=password,
        tls_profile=tls_profile,
    )
