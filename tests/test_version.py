import importlib
import tomllib
from pathlib import Path

import caddy_mcp


def test_reported_version_matches_the_released_package():
    pyproject = tomllib.loads(
        (Path(__file__).parents[1] / "pyproject.toml").read_text()
    )
    assert caddy_mcp.__version__ == pyproject["project"]["version"]


def test_every_module_reports_the_same_version():
    for name in ("api_client", "mcp_server"):
        module = importlib.import_module(f"caddy_mcp.{name}")
        assert module.__version__ == caddy_mcp.__version__, name
