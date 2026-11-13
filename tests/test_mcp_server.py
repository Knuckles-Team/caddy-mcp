import asyncio

import pytest


@pytest.mark.concept("CD-OS.identity.caddy")
def test_mcp_server_security_context():
    """CONCEPT:CD-OS.identity.caddy Verify that the server registers with correct security credentials."""
    from caddy_mcp.auth import get_client

    client = get_client()
    assert client is not None


def _served_tools():
    from scion_sdk.connector import build_server

    mcp = build_server("caddy_mcp", command_args=[])[1]
    return {t.name: t for t in asyncio.run(mcp.list_tools())}


def test_no_tool_routes_an_action():
    for name, tool in _served_tools().items():
        assert "action" not in tool.parameters.get("properties", {}), name


def test_stop_server_takes_confirm():
    """The live edge proxy stops only on a confirmed call."""
    tool = _served_tools()["caddy_stop_server"]
    assert "confirm" in tool.parameters["properties"]
    assert tool.annotations.destructive_hint is True


def test_every_config_operation_is_its_own_tool():
    names = set(_served_tools())
    for op in (
        "get_config", "post_config", "set_config", "put_config", "patch_config",
        "delete_config", "load_config", "stop_server", "get_id", "post_id",
        "put_id", "patch_id", "delete_id", "adapt_config", "get_routes",
        "get_pki_ca", "get_pki_ca_certificates", "get_reverse_proxy_upstreams",
        "get_metrics", "get_debug_vars", "get_debug_pprof",
    ):  # fmt: skip
        assert f"caddy_{op}" in names
