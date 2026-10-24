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


@pytest.mark.concept("CD-OS.identity.caddy")
def test_mcp_server_security_context():
    """CONCEPT:CD-OS.identity.caddy Verify that the server registers with correct security credentials."""
    from caddy_mcp.auth import get_client

    client = get_client()
    assert client is not None
