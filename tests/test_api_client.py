import pytest

@pytest.mark.concept("CADDY-001")
def test_api_client_basic_mock(mock_ctx):
    """CONCEPT:CADDY-001 Test basic mock initialization of client facade."""
    assert mock_ctx is not None
    assert hasattr(mock_ctx, "info")

@pytest.mark.concept("CADDY-001")
def test_api_client_endpoints(mock_ctx):
    """CONCEPT:CADDY-001 Verify endpoint configuration on dynamic client."""
    from caddy_mcp.api_client import Api
    from caddy_mcp.auth import get_client
    
    client = get_client()
    assert client is not None
    assert hasattr(client, "request")
