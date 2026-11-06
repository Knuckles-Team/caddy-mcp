# CONN-CADDY-MCP — Test specification

| Case | Fixture/action | Expected result |
| --- | --- | --- |
| VER-T1 | Read `caddy_mcp.__version__` and the `pyproject.toml` project version | They are equal |

Proof: `tests/test_version.py::test_reported_version_matches_the_released_package` (`CONN-CADDY-MCP-R001`).

| Case | Fixture/action | Expected result |
| --- | --- | --- |
| CONF-T1 | stdio, no auth, no elicitation: call load/put/patch without confirm | Typed refusal naming confirm=true; Caddy not called |
| CONF-T2 | stdio, no auth: call with confirm=true | Call runs |
| CONF-T3 | HTTP: call without then with confirm=true | Refused, then runs |

Proof: `tests/test_config_confirm.py` (`CONN-CADDY-MCP-R002`).
