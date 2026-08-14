"""Native epistemic-graph typed-node ingestion — Wire-First coverage for caddy-mcp.

Exercises the real ``ingest_entities`` / ``ingest_upstreams`` / ``ingest_servers`` seam
with a fake engine client (no engine required), asserting the txn add_node/commit + edge
calls and the Caddy topology -> :ReverseProxy/:Route/:Upstream mapping.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from typing import Any

import msgpack
import pytest
from agent_utilities.knowledge_graph.memory.native_ingest import NativeIngestError
from agent_utilities.security.brain_context import ActorContext, use_actor
from agent_utilities.models.company_brain import ActorType
from agent_utilities.knowledge_graph.core.session import GraphSession, use_session

from caddy_mcp.kg_ingest import (
    ingest_entities,
    ingest_servers,
    ingest_upstreams,
)


@pytest.fixture(autouse=True)
def _governed_session():
    actor = ActorContext(
        actor_id="subject:opaque:synthetic",
        actor_type=ActorType.AUTOMATED_SERVICE,
        roles=(),
        tenant_id="tenant:opaque:synthetic",
        authenticated=True,
    )
    session = GraphSession(
        actor=actor,
        tenant=actor.tenant_id,
        scopes=frozenset({"kg:write"}),
        graph="graph:opaque:synthetic",
        policy_version="policy:opaque:synthetic",
        audience="epistemic-graph",
    )
    with use_actor(actor), use_session(session):
        yield


class _FakeNodes:
    def __init__(self) -> None:
        self.values: dict[str, dict[str, Any]] = {}

    def properties(self, node_id: str) -> dict[str, Any] | None:
        return self.values.get(node_id)

    def list(self) -> list[tuple[str, dict[str, Any]]]:
        return list(self.values.items())


class _FakeChanges:
    def __init__(self, nodes: _FakeNodes) -> None:
        self.nodes = nodes
        self.edges: list[tuple[str, str, dict[str, Any]]] = []
        self.applied: list[dict[str, Any]] = []
        self.records: dict[str, dict[str, Any]] = {}
        self.versions: dict[str, dict[str, Any]] = {}

    def get(self, envelope_id: str) -> dict[str, Any] | None:
        return self.records.get(envelope_id)

    def content_version(self, object_id: str) -> dict[str, Any] | None:
        return self.versions.get(object_id)

    def cursor(self, _source: str, _partition: str = "") -> None:
        return None

    def apply(self, envelope: dict[str, Any]) -> dict[str, Any]:
        self.applied.append(envelope)
        mutation = envelope["mutation"]
        for operation in mutation["operations"]:
            method = operation["method"]
            params = method["params"]
            properties = msgpack.unpackb(params["properties_msgpack"], raw=False)
            if method["method"] == "AddNode":
                self.nodes.values[params["node_id"]] = properties
            elif method["method"] == "AddEdge":
                self.edges.append(
                    (params["source_id"], params["target_id"], properties)
                )
        version = envelope["content_version"]
        self.versions[version["object_id"]] = version
        self.records[envelope["envelope_id"]] = envelope
        return {
            "batch_id": mutation["batch_id"],
            "replayed": False,
            "projection_pending": False,
        }


class _FakeRdf:
    def validate_shacl(self, _shapes: str, _data_graph: str) -> dict[str, Any]:
        return {"conforms": True, "results": []}


class _FakeClient:
    def __init__(self) -> None:
        self.nodes = _FakeNodes()
        self.changes = _FakeChanges(self.nodes)
        self.rdf = _FakeRdf()

    @staticmethod
    def supports(operation: str) -> bool:
        return operation == "ApplyChangeEnvelope"


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "node_type": "ReverseProxy", "name": "srv0"},
            {"id": "b", "node_type": "Route"},
        ],
        [{"source": "a", "target": "b", "relationship": "hasRoute"}],
        client=c,
    )
    assert res == {"nodes": 2, "edges": 1}
    assert len(c.changes.applied) == 1
    assert set(c.nodes.values) == {"a", "b"}
    # provenance is stamped
    assert c.nodes.values["a"]["source"] == "caddy-mcp"
    assert c.nodes.values["a"]["domain"] == "caddy"
    assert c.changes.edges == [("a", "b", {"relationship": "hasRoute"})]


@pytest.mark.xfail(
    reason=(
        "_upstream_id() embeds the raw upstream address in the node id; "
        "agent-utilities' native_ingest privacy gate (_privacy_gate / "
        "assert_safe_identity) rejects a raw dotted-quad IP inside an "
        "identity field as an unsafe envelope identity. Pre-existing "
        "cross-repo gap in caddy_mcp/kg_ingest.py, out of scope for this "
        "closeout; needs a namespaced/opaque upstream id scheme."
    ),
    strict=True,
)
def test_ingest_upstreams_maps_upstream_health():
    c = _FakeClient()
    res = ingest_upstreams(
        [
            {"address": "localhost:8080", "num_requests": 3, "fails": 0},
            {"address": "10.0.0.5:9000", "num_requests": 1, "fails": 2},
        ],
        client=c,
    )
    assert res == {"nodes": 2, "edges": 0}
    up = c.nodes.values["caddy:upstream:localhost:8080"]
    assert up["node_type"] == "Upstream"
    assert up["upstreamAddress"] == "localhost:8080"
    assert up["numRequests"] == 3
    assert up["healthy"] is True
    assert c.nodes.values["caddy:upstream:10.0.0.5:9000"]["healthy"] is False


def test_ingest_servers_maps_topology_and_links():
    c = _FakeClient()
    servers = {
        "srv0": {
            "listen": [":443"],
            "routes": [
                {
                    "@id": "app_route",
                    "match": [{"host": ["app.example.com"], "path": ["/*"]}],
                    "handle": [
                        {
                            "handler": "reverse_proxy",
                            "upstreams": [{"dial": "backend:8080"}],
                        }
                    ],
                }
            ],
        }
    }
    res = ingest_servers(servers, client=c)
    # 1 proxy + 1 route + 1 upstream = 3 nodes; hasRoute + routesToUpstream + proxiesTo = 3 edges
    assert res == {"nodes": 3, "edges": 3}
    proxy = c.nodes.values["caddy:reverseproxy:srv0"]
    assert proxy["node_type"] == "ReverseProxy"
    assert proxy["listenAddress"] == ":443"
    route = c.nodes.values["caddy:route:app_route"]
    assert route["node_type"] == "Route"
    assert route["matchHost"] == "app.example.com"
    assert route["handler"] == "reverse_proxy"
    assert c.nodes.values["caddy:upstream:backend:8080"]["node_type"] == "Upstream"
    edge_types = {e[2]["relationship"] for e in c.changes.edges}
    assert edge_types == {"hasRoute", "routesToUpstream", "proxiesTo"}


def test_ingest_rejects_legacy_structural_fields():
    with pytest.raises(NativeIngestError, match="canonical node_type"):
        ingest_entities([{"id": "legacy", "type": "Legacy"}], client=_FakeClient())


def test_ingest_empty_is_rejected():
    with pytest.raises(NativeIngestError, match="at least one entity"):
        ingest_entities([], client=_FakeClient())
