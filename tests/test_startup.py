import sys
import pytest

def test_startup():
    # Basic import test
    import caddy_mcp
    assert caddy_mcp.__version__ == "0.15.0"
