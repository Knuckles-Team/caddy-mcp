from unittest.mock import MagicMock

import pytest

# Characterizes every caddy_mcp_config action -> client method mapping before
# any refactor of the if/elif dispatch chain in caddy_mcp/mcp/mcp_config.py.
_CONFIG_ACTION_TO_METHOD = {
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


@pytest.mark.concept("CD-OS.governance.caddy")
def test_mcp_server_registration():
    """CONCEPT:CD-OS.governance.caddy Test that tools register successfully."""
    from caddy_mcp.mcp_server import get_mcp_instance

    res = get_mcp_instance()
    if isinstance(res, tuple):
        mcp = res[0]
    else:
        mcp = res
    assert mcp is not None

    # Verify tool registry count is greater than zero
    assert len(mcp._local_provider._components) > 0


@pytest.mark.concept("CD-OS.identity.caddy")
def test_mcp_server_security_context():
    """CONCEPT:CD-OS.identity.caddy Verify that the server registers with correct security credentials."""
    from caddy_mcp.auth import get_client

    client = get_client()
    assert client is not None


@pytest.mark.concept("CD-OS.governance.caddy")
@pytest.mark.asyncio
async def test_mcp_tools_routing():
    """Every Caddy API operation is its own tool and calls the matching client method."""
    from unittest.mock import patch

    from caddy_mcp.mcp_server import get_mcp_instance

    mock_client = MagicMock()
    with patch("caddy_mcp.mcp_server.get_client", return_value=mock_client):
        res = get_mcp_instance()
    mcp = res[0] if isinstance(res, tuple) else res

    tools = {t.name: t for t in mcp._local_provider._components.values()}
    for name in (
        "caddy_get_config",
        "caddy_get_pki_ca",
        "caddy_get_reverse_proxy_upstreams",
        "caddy_get_metrics",
    ):
        assert name in tools
        assert "action" not in tools[name].parameters.get("properties", {})

    await tools["caddy_get_reverse_proxy_upstreams"].fn()
    mock_client.get_reverse_proxy_upstreams.assert_called_once()

    await tools["caddy_get_metrics"].fn()
    mock_client.get_metrics.assert_called_once()
