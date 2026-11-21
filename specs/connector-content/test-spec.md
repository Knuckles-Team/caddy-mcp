# CONN-CADDY-MCP-CONNECTOR-CONTENT — Test specification

Governing spec: [spec.md](spec.md).

| Test ID | Requirement | Proving test | Expected observation |
|---|---|---|---|
| T-001 | `CONN-CADDY-MCP-CONNECTOR-CONTENT-R001` | `tests/test_default_content_surfaces.py` | The listings include the packaged skills, ontology and prompts. |
| T-002 | `CONN-CADDY-MCP-CONNECTOR-CONTENT-R003` | `tests/test_pack_extends_core.py` | No core term is redeclared and no retired IRI base remains. |

## Rows awaiting bound tests
- `CONN-CADDY-MCP-CONNECTOR-CONTENT-R002`: planned proof `tests/test_access_contracts.py::test_competency_contracts_certified`. Expected: the route recording validates against its contract and columns routeHostname and upstreamAddress match ontology property names. Refusal: a contract whose column is not an ontology property, or lacking ac:keyField id, fails certification.
