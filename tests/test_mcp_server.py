from unittest.mock import AsyncMock, MagicMock

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
    """Verify that caddy_mcp_config, caddy_mcp_pki, and caddy_mcp_reverse_proxy tools are registered and route correctly."""
    from caddy_mcp.mcp_server import get_mcp_instance

    res = get_mcp_instance()
    mcp = res[0] if isinstance(res, tuple) else res

    # Extract registered tools from _components dict values
    tools = {t.name: t for t in mcp._local_provider._components.values()}
    assert "caddy_mcp_config" in tools
    assert "caddy_mcp_pki" in tools
    assert "caddy_mcp_reverse_proxy" in tools
    assert "caddy_mcp_debug" in tools

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
        ctx=mock_ctx,
    )
    mock_client.get_config.assert_called_once_with(path="apps")

    # Test caddy_mcp_pki action routing
    pki_tool = tools["caddy_mcp_pki"]
    await pki_tool.fn(
        action="get_pki_ca",
        params_json='{"ca_id": "local"}',
        client=mock_client,
        ctx=mock_ctx,
    )
    mock_client.get_pki_ca.assert_called_once_with(ca_id="local")

    # Test caddy_mcp_reverse_proxy action routing
    proxy_tool = tools["caddy_mcp_reverse_proxy"]
    await proxy_tool.fn(
        action="get_reverse_proxy_upstreams",
        params_json="{}",
        client=mock_client,
        ctx=mock_ctx,
    )
    mock_client.get_reverse_proxy_upstreams.assert_called_once()

    # Test caddy_mcp_debug action routing
    debug_tool = tools["caddy_mcp_debug"]
    await debug_tool.fn(
        action="get_metrics",
        params_json="{}",
        client=mock_client,
        ctx=mock_ctx,
    )
    mock_client.get_metrics.assert_called_once()
    await debug_tool.fn(
        action="get_debug_pprof",
        params_json='{"profile": "heap", "params": {"debug": 1}}',
        client=mock_client,
        ctx=mock_ctx,
    )
    mock_client.get_debug_pprof.assert_called_once_with(
        profile="heap", params={"debug": 1}
    )


@pytest.mark.concept("CD-OS.governance.caddy")
@pytest.mark.asyncio
@pytest.mark.parametrize("action,method_name", sorted(_CONFIG_ACTION_TO_METHOD.items()))
async def test_caddy_mcp_config_routes_every_action(action, method_name):
    """Characterize every caddy_mcp_config action -> client-method mapping,
    including the ``set_config`` alias onto ``post_config``, before the
    if/elif dispatch chain is refactored into a lookup table."""
    from caddy_mcp.mcp_server import get_mcp_instance

    res = get_mcp_instance()
    mcp = res[0] if isinstance(res, tuple) else res
    tools = {t.name: t for t in mcp._local_provider._components.values()}
    config_tool = tools["caddy_mcp_config"]

    mock_client = MagicMock()
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()

    await config_tool.fn(
        action=action,
        params_json='{"path": "apps"}',
        client=mock_client,
        ctx=mock_ctx,
    )
    getattr(mock_client, method_name).assert_called_once_with(path="apps")


@pytest.mark.concept("CD-OS.governance.caddy")
@pytest.mark.asyncio
async def test_caddy_mcp_config_rejects_unknown_action():
    from caddy_mcp.mcp_server import get_mcp_instance

    res = get_mcp_instance()
    mcp = res[0] if isinstance(res, tuple) else res
    tools = {t.name: t for t in mcp._local_provider._components.values()}
    config_tool = tools["caddy_mcp_config"]

    mock_client = MagicMock()
    with pytest.raises(ValueError, match="Unknown config action"):
        await config_tool.fn(
            action="not_a_real_action",
            params_json="{}",
            client=mock_client,
            ctx=None,
        )


@pytest.mark.concept("CD-OS.governance.caddy")
@pytest.mark.asyncio
async def test_caddy_mcp_config_rejects_unparseable_params():
    from caddy_mcp.mcp_server import get_mcp_instance

    res = get_mcp_instance()
    mcp = res[0] if isinstance(res, tuple) else res
    tools = {t.name: t for t in mcp._local_provider._components.values()}
    config_tool = tools["caddy_mcp_config"]

    mock_client = MagicMock()
    result = await config_tool.fn(
        action="get_config",
        params_json="not json",
        client=mock_client,
        ctx=None,
    )
    assert result == {"error": "Operation failed"}
    mock_client.get_config.assert_not_called()


@pytest.mark.concept("AU-KG.ingest.enterprise-source-extractor")
@pytest.mark.asyncio
async def test_caddy_ingest_topology_success_path():
    """Characterize caddy_ingest_topology's happy path before the fetch-helper
    extraction: both the upstreams and routes calls succeed and are ingested."""
    from unittest.mock import patch

    from caddy_mcp.mcp_server import get_mcp_instance

    res = get_mcp_instance()
    mcp = res[0] if isinstance(res, tuple) else res
    tools = {t.name: t for t in mcp._local_provider._components.values()}
    ingest_tool = tools["caddy_ingest_topology"]

    mock_client = MagicMock()
    mock_client.get_reverse_proxy_upstreams.return_value = [
        {"address": "localhost:8080", "num_requests": 1, "fails": 0}
    ]
    mock_client.get_routes.return_value = {"srv0": {"listen": [":443"], "routes": []}}
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()

    with (
        patch("caddy_mcp.kg_ingest.ingest_upstreams") as mock_ingest_upstreams,
        patch("caddy_mcp.kg_ingest.ingest_servers") as mock_ingest_servers,
    ):
        mock_ingest_upstreams.return_value = {"nodes": 1, "edges": 0}
        mock_ingest_servers.return_value = {"nodes": 1, "edges": 0}
        result = await ingest_tool.fn(client=mock_client, ctx=mock_ctx)

    assert result == {
        "upstreams_listed": 1,
        "servers_listed": 1,
        "ingested": {
            "upstreams": {"nodes": 1, "edges": 0},
            "servers": {"nodes": 1, "edges": 0},
        },
    }
    mock_ingest_upstreams.assert_called_once()
    mock_ingest_servers.assert_called_once()


@pytest.mark.concept("AU-KG.ingest.enterprise-source-extractor")
@pytest.mark.asyncio
async def test_caddy_ingest_topology_falls_back_on_fetch_errors():
    """Characterize caddy_ingest_topology's best-effort fallback: when both
    upstream and route fetches raise, ingestion is skipped and zeroed
    results are returned, without propagating the exception."""
    from caddy_mcp.mcp_server import get_mcp_instance

    res = get_mcp_instance()
    mcp = res[0] if isinstance(res, tuple) else res
    tools = {t.name: t for t in mcp._local_provider._components.values()}
    ingest_tool = tools["caddy_ingest_topology"]

    mock_client = MagicMock()
    mock_client.get_reverse_proxy_upstreams.side_effect = RuntimeError("boom")
    mock_client.get_routes.side_effect = RuntimeError("boom")
    mock_ctx = MagicMock()
    mock_ctx.info = AsyncMock()

    result = await ingest_tool.fn(client=mock_client, ctx=mock_ctx)

    assert result == {
        "upstreams_listed": 0,
        "servers_listed": 0,
        "ingested": {
            "upstreams": {"nodes": 0, "edges": 0},
            "servers": {"nodes": 0, "edges": 0},
        },
    }
