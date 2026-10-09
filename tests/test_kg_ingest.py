"""Epistemic-graph typed-node ingestion -- Wire-First coverage for caddy-mcp.

Exercises the real ``ingest_entities`` / ``ingest_upstreams`` / ``ingest_servers`` seam
against a fake ``agent_connector_sdk.ingest`` transport (no engine required). The real
SDK request builder (``agent_connector_sdk.ingest.request.build_request``) still runs,
so a malformed change set is still caught by the SDK's own contract, not re-derived
here; only the final network commit is faked.
CONCEPT:AU-KG.ingest.enterprise-source-extractor.
"""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest
from agent_connector_sdk.ingest import IngestError, KnowledgeIngest
from epistemic_graph.generated.source_ingestion import SourceIngestionRequest

from caddy_mcp.kg_ingest import (
    ingest_entities,
    ingest_servers,
    ingest_upstreams,
)


class _FakeTransport:
    """Records every submitted request; no epistemic-graph engine required."""

    def __init__(self) -> None:
        self.requests: list[SourceIngestionRequest] = []

    async def source_status(self, _connector: str, _stream: str) -> Any:
        return SimpleNamespace(accepted_checkpoint=None)

    async def submit(self, request: SourceIngestionRequest) -> Any:
        self.requests.append(request)
        return SimpleNamespace(
            affected_count=len(request.records),
            relationship_count=len(request.relationships),
        )

    async def store_blob(self, _data: bytes) -> str:
        raise AssertionError("caddy-mcp topology ingestion carries no media")


@pytest.fixture
def ingest() -> tuple[KnowledgeIngest, _FakeTransport]:
    transport = _FakeTransport()
    return KnowledgeIngest(transport, loop=None), transport


@pytest.mark.asyncio
async def test_ingest_entities_writes_nodes_and_edges(ingest):
    service, transport = ingest
    res = await ingest_entities(
        [
            {"id": "a", "node_type": "ReverseProxy", "name": "srv0"},
            {"id": "b", "node_type": "Route"},
        ],
        [{"source": "a", "target": "b", "relationship": "hasRoute"}],
        ingest=service,
    )
    assert res == {"nodes": 2, "edges": 1}
    assert len(transport.requests) == 1
    request = transport.requests[0]
    record_ids = {record.record_id for record in request.records}
    assert record_ids == {"a", "b"}
    a_record = next(r for r in request.records if r.record_id == "a")
    assert a_record.payload["name"] == "srv0"
    assert request.relationships[0].relation_reference.endswith(
        "resources/ReverseProxy/relations/hasRoute"
    )


@pytest.mark.asyncio
async def test_ingest_upstreams_maps_upstream_health(ingest):
    service, transport = ingest
    res = await ingest_upstreams(
        [
            {"address": "localhost:8080", "num_requests": 3, "fails": 0},
            {"address": "10.0.0.5:9000", "num_requests": 1, "fails": 2},
        ],
        ingest=service,
    )
    assert res == {"nodes": 2, "edges": 0}
    request = transport.requests[0]
    up = next(
        r for r in request.records if r.record_id == "caddy:upstream:localhost:8080"
    )
    assert up.payload["upstreamAddress"] == "localhost:8080"
    assert up.payload["numRequests"] == 3
    assert up.payload["healthy"] is True
    down = next(
        r for r in request.records if r.record_id == "caddy:upstream:10.0.0.5:9000"
    )
    assert down.payload["healthy"] is False


@pytest.mark.asyncio
async def test_ingest_servers_maps_topology_and_links(ingest):
    service, transport = ingest
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
    res = await ingest_servers(servers, ingest=service)
    # 1 proxy + 1 route + 1 upstream = 3 nodes; hasRoute + routesToUpstream + proxiesTo = 3 edges
    assert res == {"nodes": 3, "edges": 3}
    request = transport.requests[0]
    proxy = next(
        r for r in request.records if r.record_id == "caddy:reverseproxy:srv0"
    )
    assert proxy.payload["listenAddress"] == ":443"
    route = next(r for r in request.records if r.record_id == "caddy:route:app_route")
    assert route.payload["matchHost"] == "app.example.com"
    assert route.payload["handler"] == "reverse_proxy"
    assert any(
        r.record_id == "caddy:upstream:backend:8080" for r in request.records
    )
    relations = {rel.relation_reference.rsplit("/", 1)[-1] for rel in request.relationships}
    assert relations == {"hasRoute", "routesToUpstream", "proxiesTo"}


@pytest.mark.asyncio
async def test_ingest_rejects_legacy_structural_fields(ingest):
    service, _transport = ingest
    with pytest.raises(IngestError, match="node_type"):
        await ingest_entities([{"id": "legacy", "type": "Legacy"}], ingest=service)


@pytest.mark.asyncio
async def test_ingest_empty_is_rejected(ingest):
    service, _transport = ingest
    with pytest.raises(IngestError, match="at least one entity"):
        await ingest_entities([], ingest=service)
