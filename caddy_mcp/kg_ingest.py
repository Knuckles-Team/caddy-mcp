"""Native epistemic-graph ingestion for Caddy topology (typed graph nodes).

CONCEPT:AU-KG.ingest.enterprise-source-extractor. This is the record-source twin of
media-downloader's blob ingestion: the caddy-mcp connector natively pushes its live
topology into the ONE epistemic-graph knowledge graph as **typed OWL nodes**
(``:ReverseProxy``, ``:Route``, ``:Upstream``) + links through the required
``agent_utilities.knowledge_graph.memory.native_ingest`` authority. Node ids follow
``caddy:<class>:<externalId>``; ``node_type`` on each entity matches a class the
package's ``ontology_providers`` ``caddy.ttl`` federates.
"""

from __future__ import annotations

from typing import Any

from agent_utilities.knowledge_graph.memory.native_ingest import (
    ingest_documents as _native_ingest_documents,
)
from agent_utilities.knowledge_graph.memory.native_ingest import (
    ingest_entities as _native_ingest_entities,
)

_SOURCE = "caddy-mcp"
_DOMAIN = "caddy"


def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Write typed OWL nodes (+ edges) into epistemic-graph via the fast engine client.

    Uses canonical ``node_type`` / ``relationship`` structural fields and surfaces
    validation or engine failures as ``NativeIngestError``.
    """
    return _native_ingest_entities(
        entities,
        relationships,
        source=source,
        domain=domain,
        client=client,
        graph=graph,
    )


def ingest_documents(
    documents: list[dict[str, Any]],
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Write text records as ``:Document`` nodes (semantic-search fodder).

    Each doc: ``{"id":..., "text":..., "title"?:..., "source_uri"?:..., ...props}``.
    Delegates directly to the required native ingestion authority.
    """
    return _native_ingest_documents(
        documents, source=source, domain=domain, client=client, graph=graph
    )


# ---------------------------------------------------------------------------
# Domain mappers: Caddy live topology -> typed :ReverseProxy/:Route/:Upstream nodes.
# ---------------------------------------------------------------------------


def _upstream_id(address: str) -> str:
    return f"caddy:upstream:{address}"


def ingest_upstreams(
    upstreams: list[dict[str, Any]],
    *,
    client: Any | None = None,
    graph: str | None = None,
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
    return ingest_entities(entities, None, client=client, graph=graph)


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


def ingest_servers(
    servers: dict[str, Any],
    *,
    client: Any | None = None,
    graph: str | None = None,
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
    return ingest_entities(entities, relationships, client=client, graph=graph)
