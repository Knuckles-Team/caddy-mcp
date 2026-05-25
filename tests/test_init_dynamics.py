import pytest
@pytest.mark.concept("CADDY-001")
def test_init_dynamics():
    import caddy_mcp

    assert caddy_mcp._MCP_AVAILABLE is True
