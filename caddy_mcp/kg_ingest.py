"""Epistemic-graph ingestion for Caddy topology (typed graph nodes).

CONCEPT:AU-KG.ingest.enterprise-source-extractor. The caddy-mcp connector pushes its
live topology into the ONE epistemic-graph knowledge graph as **typed OWL nodes**
(``:ReverseProxy``, ``:Route``, ``:Upstream``) + links through
``agent_connector_sdk.ingest`` -- the generated ``SourceIngest`` client, not a local
ingestion helper. Node ids follow ``caddy:<class>:<externalId>``; ``node_type`` on
each entity matches a class the package's ``ontology_providers`` ``caddy.ttl``
federates.
"""

from __future__ import annotations

from typing import Any

from agent_connector_sdk.ingest import (
    ChangeSet,
    Document,
    Entity,
    IngestBinding,
    IngestError,
    KnowledgeIngest,
    Relationship,
    current_ingest,
)

_BINDING = IngestBinding(connector="caddy-mcp", stream="caddy")

_ENTITY_RESERVED_KEYS = frozenset({"id", "node_type"})
_RELATIONSHIP_RESERVED_KEYS = frozenset({"source", "target", "relationship"})


def _to_entity(record: dict[str, Any]) -> Entity:
    return Entity(
        id=record.get("id"),
        node_type=record.get("node_type"),
        properties={
            key: value
            for key, value in record.items()
            if key not in _ENTITY_RESERVED_KEYS
        },
    )


def _to_relationship(record: dict[str, Any]) -> Relationship:
    properties = {
        key: value
        for key, value in record.items()
        if key not in _RELATIONSHIP_RESERVED_KEYS
    }
    return Relationship(
        source=record["source"],
        target=record["target"],
        relationship=record["relationship"],
        properties=properties or None,
    )


async def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
    """Write typed OWL nodes (+ edges) into epistemic-graph via the SDK ingest facade.

    Uses canonical ``node_type`` / ``relationship`` structural fields and surfaces
    a malformed change set or a refused commit as ``IngestError``.
    """
    if not entities:
        raise IngestError("ingest_entities needs at least one entity")
    change_set = ChangeSet(
        entities=tuple(_to_entity(entity) for entity in entities),
        relationships=tuple(
            _to_relationship(relationship) for relationship in relationships or ()
        ),
    )
    service = ingest or current_ingest()
    receipt = await service.submit(_BINDING, change_set)
    return {"nodes": receipt.affected_count, "edges": receipt.relationship_count}


async def ingest_documents(
    documents: list[dict[str, Any]],
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
    """Write text records as ``:Document`` nodes (semantic-search fodder).

    Each doc: ``{"id":..., "text":..., "title"?:..., "source_uri"?:..., ...props}``.
    """
    if not documents:
        raise IngestError("ingest_documents needs at least one document")
    change_set = ChangeSet(
        documents=tuple(
            Document(
                id=doc["id"],
                text=doc["text"],
                title=doc.get("title"),
                source_uri=doc.get("source_uri"),
                properties={
                    key: value
                    for key, value in doc.items()
                    if key not in {"id", "text", "title", "source_uri"}
                },
            )
            for doc in documents
        )
    )
    service = ingest or current_ingest()
    receipt = await service.submit(_BINDING, change_set)
    return {"nodes": receipt.affected_count, "edges": receipt.relationship_count}


# ---------------------------------------------------------------------------
# Domain mappers: Caddy live topology -> typed :ReverseProxy/:Route/:Upstream nodes.
# ---------------------------------------------------------------------------


def _upstream_id(address: str) -> str:
    return f"caddy:upstream:{address}"


async def ingest_upstreams(
    upstreams: list[dict[str, Any]],
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
    """Map ``get_reverse_proxy_upstreams`` records -> ``:Upstream`` nodes and ingest.

    Each record: ``{"address": host:port, "num_requests": n, "fails": m, ...}``.
    """
    entities: list[dict[str, Any]] = []
    for up in upstreams or []:
        address = up.get("address")
        if not address:
            continue
        fails = up.get("fails")
        entities.append(
            {
                "id": _upstream_id(address),
                "node_type": "Upstream",
                "upstreamAddress": address,
                "numRequests": up.get("num_requests"),
                "fails": fails,
                "healthy": (fails == 0) if isinstance(fails, int) else None,
                "externalToolId": address,
            }
        )
    return await ingest_entities(entities, None, ingest=ingest)


def _extract_hosts(matchers: Any) -> list[str]:
    hosts: list[str] = []
    for m in matchers or []:
        if isinstance(m, dict):
            for h in m.get("host") or []:
                hosts.append(str(h))
    return hosts


def _extract_paths(matchers: Any) -> list[str]:
    paths: list[str] = []
    for m in matchers or []:
        if isinstance(m, dict):
            for p in m.get("path") or []:
                paths.append(str(p))
    return paths


def _upstream_dial_addresses(handler: dict[str, Any]) -> list[str]:
    if handler.get("handler") != "reverse_proxy":
        return []
    return [
        str(u["dial"])
        for u in handler.get("upstreams") or []
        if isinstance(u, dict) and u.get("dial")
    ]


def _extract_upstreams(handlers: Any) -> tuple[str | None, list[str]]:
    """Return ``(primary_handler_kind, [upstream dial addresses])`` for a route's handlers."""
    kind: str | None = None
    addresses: list[str] = []
    for h in handlers or []:
        if not isinstance(h, dict):
            continue
        if kind is None:
            kind = h.get("handler")
        addresses.extend(_upstream_dial_addresses(h))
    return kind, addresses


def _server_entity(name: str, server: dict[str, Any], proxy_id: str) -> dict[str, Any]:
    listen = server.get("listen") or []
    return {
        "id": proxy_id,
        "node_type": "ReverseProxy",
        "name": name,
        "listenAddress": ",".join(str(a) for a in listen) or None,
        "externalToolId": name,
    }


def _upstream_nodes(
    route_id: str, proxy_id: str, addresses: list[str]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    for address in addresses:
        upstream_id = _upstream_id(address)
        entities.append(
            {
                "id": upstream_id,
                "node_type": "Upstream",
                "upstreamAddress": address,
                "externalToolId": address,
            }
        )
        relationships.append(
            {
                "source": route_id,
                "target": upstream_id,
                "relationship": "routesToUpstream",
            }
        )
        relationships.append(
            {"source": proxy_id, "target": upstream_id, "relationship": "proxiesTo"}
        )
    return entities, relationships


def _route_nodes(
    proxy_id: str, name: str, idx: int, route: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    rid = route.get("@id") or f"{name}[{idx}]"
    route_id = f"caddy:route:{rid}"
    hosts = _extract_hosts(route.get("match"))
    paths = _extract_paths(route.get("match"))
    kind, addresses = _extract_upstreams(route.get("handle"))

    entities: list[dict[str, Any]] = [
        {
            "id": route_id,
            "node_type": "Route",
            "routeId": str(rid),
            "matchHost": ",".join(hosts) or None,
            "matchPath": ",".join(paths) or None,
            "handler": kind,
            "externalToolId": str(rid),
        }
    ]
    relationships: list[dict[str, Any]] = [
        {"source": proxy_id, "target": route_id, "relationship": "hasRoute"}
    ]
    upstream_entities, upstream_relationships = _upstream_nodes(
        route_id, proxy_id, addresses
    )
    entities.extend(upstream_entities)
    relationships.extend(upstream_relationships)
    return entities, relationships


def _server_nodes(
    name: str, server: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    proxy_id = f"caddy:reverseproxy:{name}"
    entities: list[dict[str, Any]] = [_server_entity(name, server, proxy_id)]
    relationships: list[dict[str, Any]] = []
    for idx, route in enumerate(server.get("routes") or []):
        if not isinstance(route, dict):
            continue
        route_entities, route_relationships = _route_nodes(proxy_id, name, idx, route)
        entities.extend(route_entities)
        relationships.extend(route_relationships)
    return entities, relationships


async def ingest_servers(
    servers: dict[str, Any],
    *,
    ingest: KnowledgeIngest | None = None,
) -> dict[str, int]:
    """Map the ``apps/http/servers`` config -> ``:ReverseProxy`` + ``:Route`` (+ ``:Upstream``).

    ``servers``: ``{server_name: {"listen": [...], "routes": [...]}}`` (the shape returned
    by ``get_routes``). Emits a ``:ReverseProxy`` per server, a ``:Route`` per route with
    ``:hasRoute`` links, and ``:routesToUpstream`` links into the ``:Upstream`` backends
    each reverse_proxy route dials.
    """
    entities: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []
    for name, server in (servers or {}).items():
        if not isinstance(server, dict):
            continue
        server_entities, server_relationships = _server_nodes(name, server)
        entities.extend(server_entities)
        relationships.extend(server_relationships)
    return await ingest_entities(entities, relationships, ingest=ingest)
