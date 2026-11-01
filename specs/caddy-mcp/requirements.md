# CONN-CADDY-MCP — Requirements

Every requirement this specification owns, with the proof that closes it. Delivery state and
public evidence for each ID are recorded in [`status.json`](status.json); this file defines what
each ID means. The design is in [`spec.md`](spec.md) and [`plan.md`](plan.md), the test contract
in [`test-spec.md`](test-spec.md), and the work order in [`tasks.md`](tasks.md).

| ID | Requirement | Verification |
|---|---|---|
| `CONN-CADDY-MCP-R001` | **Connector reports its released version.** `caddy_mcp.__version__` equals the released `pyproject.toml` version and the bump configuration updates both. Caller chain: the `caddy-mcp` console script (pyproject.toml, scion_sdk.cli:serve) loads `caddy_mcp:connector` (caddy_mcp/__init__.py) whose Api is caddy_mcp/api_client.py::Api, and `__version__ = _v("caddy-mcp")` at caddy_mcp/api_client.py:8 reads the installed package metadata; tests/test_version.py does not exist yet (planned). Shape: caddy_mcp/api_client.py::__version__ already comes from importlib.metadata.version("caddy-mcp"), so it follows the pyproject.toml version of 2.3.8 with no second copy; the planned tests/test_version.py compares the two and no bump configuration exists to update. | `tests/test_version.py::test_reported_version_matches_the_released_package` |
