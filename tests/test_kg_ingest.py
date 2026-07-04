"""Native epistemic-graph typed-node ingestion — Wire-First coverage for caddy-mcp.

Exercises the real ``ingest_entities`` / ``ingest_upstreams`` / ``ingest_servers`` seam
with a fake engine client (no engine required), asserting the txn add_node/commit + edge
calls and the Caddy topology -> :ReverseProxy/:Route/:Upstream mapping.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from caddy_mcp.kg_ingest import (
    ingest_entities,
    ingest_servers,
    ingest_upstreams,
)


class _FakeTxn:
    def __init__(self):
        self.nodes = {}
        self.committed = False

    def begin(self, graph=None):
        self.graph = graph
        return "txn-1"

    def add_node(self, txn, node_id, props):
        self.nodes[node_id] = props

    def commit(self, txn):
        self.committed = True
        return True


class _FakeEdges:
    def __init__(self):
        self.edges = []

    def add(self, src, dst, props):
        self.edges.append((src, dst, props))


class _FakeClient:
    def __init__(self):
        self.txn = _FakeTxn()
        self.edges = _FakeEdges()


def test_ingest_entities_writes_nodes_and_edges():
    c = _FakeClient()
    res = ingest_entities(
        [
            {"id": "a", "type": "ReverseProxy", "name": "srv0"},
            {"id": "b", "type": "Route"},
        ],
        [{"source": "a", "target": "b", "type": "hasRoute"}],
        client=c,
        graph="__commons__",
    )
    assert res == {"nodes": 2, "edges": 1}
    assert c.txn.committed is True
    assert set(c.txn.nodes) == {"a", "b"}
    # provenance is stamped
    assert c.txn.nodes["a"]["source"] == "caddy-mcp"
    assert c.txn.nodes["a"]["domain"] == "caddy"
    assert c.edges.edges == [("a", "b", {"type": "hasRoute"})]


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
    assert up["type"] == "Upstream"
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
    assert proxy["type"] == "ReverseProxy"
    assert proxy["listenAddress"] == ":443"
    route = c.txn.nodes["caddy:route:app_route"]
    assert route["type"] == "Route"
    assert route["matchHost"] == "app.example.com"
    assert route["handler"] == "reverse_proxy"
    assert c.txn.nodes["caddy:upstream:backend:8080"]["type"] == "Upstream"
    edge_types = {e[2]["type"] for e in c.edges.edges}
    assert edge_types == {"hasRoute", "routesToUpstream", "proxiesTo"}


def test_ingest_noops_without_engine():
    # No injected client + no reachable engine -> clean no-op.
    assert ingest_entities([{"id": "a", "type": "ReverseProxy"}]) is None


def test_ingest_empty_is_noop():
    assert ingest_entities([], client=_FakeClient()) is None
    assert ingest_upstreams([], client=_FakeClient()) is None
    assert ingest_servers({}, client=_FakeClient()) is None
