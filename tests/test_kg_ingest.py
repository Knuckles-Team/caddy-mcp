"""Native epistemic-graph typed-node ingestion — Wire-First coverage for caddy-mcp.

Exercises the real ``ingest_entities`` / ``ingest_upstreams`` / ``ingest_servers`` seam
with a fake engine client (no engine required), asserting the txn add_node/commit + edge
calls and the Caddy topology -> :ReverseProxy/:Route/:Upstream mapping.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

import pytest
from agent_utilities.knowledge_graph.memory.native_ingest import NativeIngestError

from caddy_mcp.kg_ingest import (
    ingest_entities,
    ingest_servers,
    ingest_upstreams,
)


class _FakeTxn:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.committed = False

    def begin(self, graph=None):
        self.graph = graph
        return "txn-1"

    def add_node(self, txn, node_id, props):
        self.nodes[node_id] = props

    def add_edge(self, txn, src, dst, props):
        self.edges.append((src, dst, props))

    def commit(self, txn):
        self.committed = True
        return True


class _FakeClient:
    def __init__(self):
        self.txn = _FakeTxn()


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "node_type": "ReverseProxy", "name": "srv0"},
            {"id": "b", "node_type": "Route"},
        ],
        [{"source": "a", "target": "b", "relationship": "hasRoute"}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    assert c.txn.committed is True
    assert set(c.txn.nodes) == {"a", "b"}
    # provenance is stamped
    assert c.txn.nodes["a"]["source"] == "caddy-mcp"
    assert c.txn.nodes["a"]["domain"] == "caddy"
    assert c.txn.edges == [("a", "b", {"relationship": "hasRoute"})]


def test_ingest_upstreams_maps_upstream_health():
    c = _FakeClient()
    res = ingest_upstreams(
        [
            {"address": "localhost:8080", "num_requests": 3, "fails": 0},
            {"address": "10.0.0.5:9000", "num_requests": 1, "fails": 2},
        ],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 0}
    up = c.txn.nodes["caddy:upstream:localhost:8080"]
    assert up["node_type"] == "Upstream"
    assert up["upstreamAddress"] == "localhost:8080"
    assert up["numRequests"] == 3
    assert up["healthy"] is True
    assert c.txn.nodes["caddy:upstream:10.0.0.5:9000"]["healthy"] is False


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
    res = ingest_servers(servers, client=c, graph="__commons__")
    # 1 proxy + 1 route + 1 upstream = 3 nodes; hasRoute + routesToUpstream + proxiesTo = 3 edges
    assert res == {"nodes": 3, "edges": 3}
    proxy = c.txn.nodes["caddy:reverseproxy:srv0"]
    assert proxy["node_type"] == "ReverseProxy"
    assert proxy["listenAddress"] == ":443"
    route = c.txn.nodes["caddy:route:app_route"]
    assert route["node_type"] == "Route"
    assert route["matchHost"] == "app.example.com"
    assert route["handler"] == "reverse_proxy"
    assert c.txn.nodes["caddy:upstream:backend:8080"]["node_type"] == "Upstream"
    edge_types = {e[2]["relationship"] for e in c.txn.edges}
    assert edge_types == {"hasRoute", "routesToUpstream", "proxiesTo"}


def test_ingest_rejects_legacy_structural_fields():
    with pytest.raises(NativeIngestError, match="canonical node_type"):
        ingest_entities([{"id": "legacy", "type": "Legacy"}], client=_FakeClient())


def test_ingest_empty_is_rejected():
    with pytest.raises(NativeIngestError, match="at least one entity"):
        ingest_entities([], client=_FakeClient())
