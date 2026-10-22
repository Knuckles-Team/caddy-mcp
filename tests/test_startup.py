import pytest


@pytest.mark.concept("CADDY-002")
def test_startup():
    # Basic import test
    import caddy_mcp

    assert caddy_mcp.__version__  # value is checked in test_version.py
