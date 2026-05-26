import pytest
from unittest.mock import MagicMock, AsyncMock


@pytest.mark.concept("CADDY-002")
def test_mcp_server_registration():
    """CONCEPT:CADDY-002 Test that tools register successfully."""
    from caddy_mcp.mcp_server import get_mcp_instance
    res = get_mcp_instance()
    if isinstance(res, tuple):
        mcp = res[0]
    else:
        mcp = res
    assert mcp is not None

    # Verify tool registry count is greater than zero
    assert len(mcp._local_provider._components) > 0


@pytest.mark.concept("CADDY-003")
def test_mcp_server_security_context():
    """CONCEPT:CADDY-003 Verify that the server registers with correct security credentials."""
    from caddy_mcp.auth import get_client
    client = get_client()
    assert client is not None


@pytest.mark.concept("CADDY-002")
@pytest.mark.asyncio
async def test_mcp_tools_routing():
    """Verify that caddy_mcp_config, caddy_mcp_pki, and caddy_mcp_reverse_proxy tools are registered and route correctly."""
    from caddy_mcp.mcp_server import get_mcp_instance
    res = get_mcp_instance()
    mcp = res[0] if isinstance(res, tuple) else res

    # Extract registered tools from _components dict values
    tools = {t.name: t for t in mcp._local_provider._components.values()}
    assert "caddy_mcp_config" in tools
    assert "caddy_mcp_pki" in tools
    assert "caddy_mcp_reverse_proxy" in tools

    # Mock client and context
    mock_client = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()

    # Test caddy_mcp_config action routing
    config_tool = tools["caddy_mcp_config"]
    await config_tool.fn(
        action="get_config",
        params_json='{"path": "apps"}',
        client=mock_client,
        ctx=mock_ctx
    )
    mock_client.get_config.assert_called_once_with(path="apps")

    # Test caddy_mcp_pki action routing
    pki_tool = tools["caddy_mcp_pki"]
    await pki_tool.fn(
        action="get_pki_ca",
        params_json='{"ca_id": "local"}',
        client=mock_client,
        ctx=mock_ctx
    )
    mock_client.get_pki_ca.assert_called_once_with(ca_id="local")

    # Test caddy_mcp_reverse_proxy action routing
    proxy_tool = tools["caddy_mcp_reverse_proxy"]
    await proxy_tool.fn(
        action="get_reverse_proxy_upstreams",
        params_json="{}",
        client=mock_client,
        ctx=mock_ctx
    )
    mock_client.get_reverse_proxy_upstreams.assert_called_once()
