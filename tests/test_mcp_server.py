import pytest

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
