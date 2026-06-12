from unittest.mock import MagicMock, patch

import pytest

from caddy_mcp.api_client import Api


@pytest.mark.concept("CADDY-001")
def test_api_client_basic_mock(mock_ctx):
    """CONCEPT:CADDY-001 Test basic mock initialization of client facade."""
    assert mock_ctx is not None
    assert hasattr(mock_ctx, "info")


@pytest.mark.concept("CADDY-001")
def test_api_client_endpoints(mock_ctx):
    """CONCEPT:CADDY-001 Verify endpoint configuration on dynamic client."""
    from caddy_mcp.auth import get_client

    client = get_client()
    assert client is not None
    assert hasattr(client, "request")


@pytest.mark.concept("CADDY-001")
def test_api_client_full_endpoints():
    """Test all the newly added Caddy REST API endpoints with mocked HTTP sessions."""
    client = Api(base_url="http://localhost:2019")

    with patch.object(client._session, "request") as mock_request:
        # Mock successful JSON response with ETag header
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {"ETag": '"abc-123"'}
        mock_response.text = '{"status": "success"}'
        mock_response.json.return_value = {"status": "success"}
        mock_request.return_value = mock_response

        # Test load_config
        client.load_config({"apps": {}}, config_adapter="json5", force_reload=True)
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "POST"
        assert kwargs["url"] == "http://localhost:2019/load"
        assert kwargs["headers"] == {
            "Content-Type": "application/json5",
            "Cache-Control": "must-revalidate",
        }
        assert kwargs["json"] == {"apps": {}}
        assert client.last_etag == '"abc-123"'

        # Test stop_server
        client.stop_server()
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "POST"
        assert kwargs["url"] == "http://localhost:2019/stop"
        assert kwargs["headers"] == {"Content-Type": "application/json"}

        # Test get_config
        client.get_config("apps/http")
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "http://localhost:2019/config/apps/http"
        assert kwargs["headers"] == {"Content-Type": "application/json"}

        # Test post_config / set_config
        client.post_config("apps/http", {"server": "test"}, if_match='"abc-123"')
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "POST"
        assert kwargs["url"] == "http://localhost:2019/config/apps/http"
        assert kwargs["headers"] == {
            "Content-Type": "application/json",
            "If-Match": '"abc-123"',
        }
        assert kwargs["json"] == {"server": "test"}

        # Test put_config
        client.put_config("apps/http", {"server": "test"})
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "PUT"
        assert kwargs["url"] == "http://localhost:2019/config/apps/http"
        assert kwargs["headers"] == {"Content-Type": "application/json"}
        assert kwargs["json"] == {"server": "test"}

        # Test patch_config
        client.patch_config("apps/http", {"server": "test"})
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "PATCH"
        assert kwargs["url"] == "http://localhost:2019/config/apps/http"
        assert kwargs["headers"] == {"Content-Type": "application/json"}
        assert kwargs["json"] == {"server": "test"}

        # Test delete_config
        client.delete_config("apps/http")
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "DELETE"
        assert kwargs["url"] == "http://localhost:2019/config/apps/http"
        assert kwargs["headers"] == {"Content-Type": "application/json"}

        # Test get_id
        client.get_id("my_proxy")
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "http://localhost:2019/id/my_proxy"
        assert kwargs["headers"] == {"Content-Type": "application/json"}

        # Test post_id
        client.post_id("my_proxy", {"new": "val"})
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "POST"
        assert kwargs["url"] == "http://localhost:2019/id/my_proxy"
        assert kwargs["headers"] == {"Content-Type": "application/json"}
        assert kwargs["json"] == {"new": "val"}

        # Test put_id
        client.put_id("my_proxy", {"new": "val"})
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "PUT"
        assert kwargs["url"] == "http://localhost:2019/id/my_proxy"
        assert kwargs["headers"] == {"Content-Type": "application/json"}
        assert kwargs["json"] == {"new": "val"}

        # Test patch_id
        client.patch_id("my_proxy", {"new": "val"})
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "PATCH"
        assert kwargs["url"] == "http://localhost:2019/id/my_proxy"
        assert kwargs["headers"] == {"Content-Type": "application/json"}
        assert kwargs["json"] == {"new": "val"}

        # Test delete_id
        client.delete_id("my_proxy")
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "DELETE"
        assert kwargs["url"] == "http://localhost:2019/id/my_proxy"
        assert kwargs["headers"] == {"Content-Type": "application/json"}

        # Test adapt_config
        client.adapt_config("Caddyfile", config_adapter="caddyfile")
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "POST"
        assert kwargs["url"] == "http://localhost:2019/adapt"
        assert kwargs["headers"] == {"Content-Type": "text/caddyfile"}
        assert kwargs["data"] == "Caddyfile"

        # Test get_pki_ca
        client.get_pki_ca("local")
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "http://localhost:2019/pki/ca/local"
        assert kwargs["headers"] == {"Content-Type": "application/json"}

        # Test get_pki_ca_certificates
        client.get_pki_ca_certificates("local")
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "http://localhost:2019/pki/ca/local/certificates"
        assert kwargs["headers"] == {"Content-Type": "application/json"}

        # Test get_reverse_proxy_upstreams
        client.get_reverse_proxy_upstreams()
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "http://localhost:2019/reverse_proxy/upstreams"
        assert kwargs["headers"] == {"Content-Type": "application/json"}

        # Test get_metrics
        client.get_metrics()
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "http://localhost:2019/metrics"

        # Test get_debug_vars
        client.get_debug_vars()
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "http://localhost:2019/debug/vars"

        # Test get_debug_pprof (index)
        client.get_debug_pprof()
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "http://localhost:2019/debug/pprof/"

        # Test get_debug_pprof (named profile with query params)
        client.get_debug_pprof("heap", params={"debug": 1})
        _, kwargs = mock_request.call_args
        assert kwargs["method"] == "GET"
        assert kwargs["url"] == "http://localhost:2019/debug/pprof/heap"
        assert kwargs["params"] == {"debug": 1}
