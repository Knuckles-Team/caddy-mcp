"""Native epistemic-graph ingestion for Caddy topology (typed graph nodes).

CONCEPT:AU-KG.ingest.enterprise-source-extractor. This is the record-source twin of
media-downloader's blob ingestion: the caddy-mcp connector natively pushes its live
topology into the ONE epistemic-graph knowledge graph as **typed OWL nodes**
(``:ReverseProxy``, ``:Route``, ``:Upstream``) + links, using the lightweight engine
client (``GraphComputeEngine()._client`` + ``txn``) — the same fast client the blob
``MediaStore`` uses, NOT the heavy in-process ingestion engine.

It is a thin mapper over the shared primitive
``agent_utilities.knowledge_graph.memory.native_ingest``: that import is GUARDED, and
when it is absent (the primitive is not yet in the installed agent_utilities) a
self-contained txn fallback drives the same write path. Everything is
dependency-/engine-guarded — with no KG stack or no reachable engine every entry point
**no-ops** (returns ``None``), so the connector keeps working with zero KG infra. Node
ids follow ``caddy:<class>:<externalId>``; ``type`` on each entity matches a class the
package's ``ontology_providers`` ``caddy.ttl`` federates.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger("caddy_mcp.kg")

_SOURCE = "caddy-mcp"
_DOMAIN = "caddy"
_DEFAULT_GRAPH = "__commons__"

# ---------------------------------------------------------------------------
# Shared-primitive delegation (guarded) with a self-contained txn fallback.
# ---------------------------------------------------------------------------
try:  # pragma: no cover - trivial import guard
    from agent_utilities.knowledge_graph.memory.native_ingest import (
        ingest_entities as _shared_ingest_entities,
    )

    _HAVE_SHARED = True
except Exception as _e:  # noqa: BLE001 — primitive not installed yet
    logger.debug("caddy kg ingest: shared primitive unavailable: %s", _e)
    _HAVE_SHARED = False


def _client() -> tuple[Any | None, str]:
    """Return ``(engine_client, graph_name)`` or ``(None, "")`` when unavailable."""
    try:
        from agent_utilities.knowledge_graph.core.graph_compute import (
            GraphComputeEngine,
        )
    except Exception as e:  # noqa: BLE001 — KG stack absent
        logger.debug("caddy kg ingest unavailable (import): %s", e)
        return None, ""
    try:
        engine = GraphComputeEngine()
        client = getattr(engine, "_client", None)
        if client is None:
            return None, ""
        return client, (getattr(engine, "graph_name", None) or _DEFAULT_GRAPH)
    except Exception as e:  # noqa: BLE001 — engine unreachable
        logger.debug("caddy kg ingest: engine unreachable: %s", e)
        return None, ""


def _fallback_ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None,
    *,
    source: str,
    domain: str,
    client: Any | None,
    graph: str | None,
) -> dict[str, int] | None:
    """Self-contained txn write path (used when the shared primitive is absent)."""
    entities = [e for e in (entities or []) if e.get("id")]
    if not entities:
        return None
    if client is None:
        client, graph = _client()
    if client is None:
        return None
    graph = graph or _DEFAULT_GRAPH

    try:
        txn = client.txn.begin(graph=graph)
        for ent in entities:
            props = {k: v for k, v in ent.items() if k != "id" and v is not None}
            props.setdefault("source", source)
            props.setdefault("domain", domain)
            client.txn.add_node(txn, ent["id"], props)
        committed = client.txn.commit(txn)
    except Exception as e:  # noqa: BLE001 — engine/txn failure is non-fatal
        logger.warning("caddy kg ingest: txn failed: %s", e)
        return None
    if not committed:
        logger.warning("caddy kg ingest: txn not committed (conflict)")
        return None

    edges = 0
    for rel in relationships or []:
        try:
            client.edges.add(
                rel["source"], rel["target"], {"type": rel.get("type", "RELATED")}
            )
            edges += 1
        except Exception as e:  # noqa: BLE001 — pure edge link, best-effort
            logger.debug("caddy kg ingest: edge skipped: %s", e)

    logger.info("caddy kg ingest: wrote %d nodes, %d edges", len(entities), edges)
    return {"nodes": len(entities), "edges": edges}


def ingest_entities(
    entities: list[dict[str, Any]],
    relationships: list[dict[str, Any]] | None = None,
    *,
    source: str = _SOURCE,
    domain: str = _DOMAIN,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
    """Write typed OWL nodes (+ edges) into epistemic-graph via the fast engine client.

    ``entities``: ``[{"id":..., "type":<owl:Class>, ...props}]``.
    ``relationships``: ``[{"source":id, "target":id, "type":rel}]``.
    Returns ``{"nodes":n, "edges":m}`` or ``None`` (no engine / failure; never raises).
    Delegates to the shared ``native_ingest`` primitive when installed, else a
    self-contained txn fallback. ``client``/``graph`` may be injected (tests).
    """
    if not entities:
        return None
    if _HAVE_SHARED:
        return _shared_ingest_entities(
            entities,
            relationships,
            source=source,
            domain=domain,
            client=client,
            graph=graph,
        )
    return _fallback_ingest_entities(
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
) -> dict[str, int] | None:
    """Write text records as ``:Document`` nodes (semantic-search fodder).

    Each doc: ``{"id":..., "text":..., "title"?:..., "source_uri"?:..., ...props}``.
    Delegates to the shared primitive when available, else maps to typed nodes via the
    self-contained fallback. Returns ``{"nodes":n, "edges":0}`` or ``None``.
    """
    if not documents:
        return None
    if _HAVE_SHARED:
        try:
            from agent_utilities.knowledge_graph.memory.native_ingest import (
                ingest_documents as _shared_ingest_documents,
            )

            return _shared_ingest_documents(
                documents, source=source, domain=domain, client=client, graph=graph
            )
        except Exception as e:  # noqa: BLE001
            logger.debug("caddy kg ingest: shared documents unavailable: %s", e)

    nodes: list[dict[str, Any]] = []
    for doc in documents:
        did = doc.get("id")
        text = doc.get("text") or doc.get("content")
        if not did or not text:
            continue
        node = {k: v for k, v in doc.items() if k != "content" and v is not None}
        node["id"] = did
        node["type"] = "Document"
        node["text"] = text
        nodes.append(node)
    return _fallback_ingest_entities(
        nodes, None, source=source, domain=domain, client=client, graph=graph
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
) -> dict[str, int] | None:
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
                "type": "Upstream",
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


def _extract_upstreams(handlers: Any) -> tuple[str | None, list[str]]:
    """Return ``(primary_handler_kind, [upstream dial addresses])`` for a route's handlers."""
    kind: str | None = None
    addresses: list[str] = []
    for h in handlers or []:
        if not isinstance(h, dict):
            continue
        if kind is None:
            kind = h.get("handler")
        if h.get("handler") == "reverse_proxy":
            for u in h.get("upstreams") or []:
                if isinstance(u, dict) and u.get("dial"):
                    addresses.append(str(u["dial"]))
    return kind, addresses


def ingest_servers(
    servers: dict[str, Any],
    *,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int] | None:
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
        proxy_id = f"caddy:reverseproxy:{name}"
        listen = server.get("listen") or []
        entities.append(
            {
                "id": proxy_id,
                "type": "ReverseProxy",
                "name": name,
                "listenAddress": ",".join(str(a) for a in listen) or None,
                "externalToolId": name,
            }
        )
        for idx, route in enumerate(server.get("routes") or []):
            if not isinstance(route, dict):
                continue
            rid = route.get("@id") or f"{name}[{idx}]"
            route_id = f"caddy:route:{rid}"
            hosts = _extract_hosts(route.get("match"))
            paths = _extract_paths(route.get("match"))
            kind, addresses = _extract_upstreams(route.get("handle"))
            entities.append(
                {
                    "id": route_id,
                    "type": "Route",
                    "routeId": str(rid),
                    "matchHost": ",".join(hosts) or None,
                    "matchPath": ",".join(paths) or None,
                    "handler": kind,
                    "externalToolId": str(rid),
                }
            )
            relationships.append(
                {"source": proxy_id, "target": route_id, "type": "hasRoute"}
            )
            for address in addresses:
                entities.append(
                    {
                        "id": _upstream_id(address),
                        "type": "Upstream",
                        "upstreamAddress": address,
                        "externalToolId": address,
                    }
                )
                relationships.append(
                    {
                        "source": route_id,
                        "target": _upstream_id(address),
                        "type": "routesToUpstream",
                    }
                )
                relationships.append(
                    {
                        "source": proxy_id,
                        "target": _upstream_id(address),
                        "type": "proxiesTo",
                    }
                )
    return ingest_entities(entities, relationships, client=client, graph=graph)
