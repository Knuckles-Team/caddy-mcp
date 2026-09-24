"""EH-410: CrowdSec edge decisions as a security-audit feed.

CrowdSec (edge-ingress) decides which scope values to ban or challenge. The
Local API's bouncer stream (``GET /v1/decisions/stream``) returns the decisions
added and deleted since the last poll; this module maps them to
``:IntrusionDecision`` nodes through agent-utilities' ``AuditPseudonymizer``.

Operator ruling 2026-09-24: a ban TARGET is kept whole -- the decision is about
exactly that address -- while any other identity would be pseudonymized. A
deleted (expired/revoked) decision is re-written with ``active = false``.
"""

from __future__ import annotations

from typing import Any

from caddy_mcp import kg_ingest

#: The bouncer stream endpoint of the CrowdSec Local API.
STREAM_PATH = "/v1/decisions/stream"
_POLICY = {
    "keep": ("id", "origin", "type", "scope", "scenario", "duration"),
    "whole_ips": ("value",),
}


def fetch_decisions(
    lapi_url: str, bouncer_key: str, *, startup: bool, timeout: float = 30.0
) -> dict[str, list[dict[str, Any]]]:
    """One bouncer-stream poll: ``{"new": [...], "deleted": [...]}``."""
    import requests

    response = requests.get(
        lapi_url.rstrip("/") + STREAM_PATH,
        params={"startup": "true" if startup else "false"},
        headers={"X-Api-Key": bouncer_key},
        timeout=timeout,
    )
    response.raise_for_status()
    body = response.json() or {}
    return {
        "new": [d for d in body.get("new") or [] if isinstance(d, dict)],
        "deleted": [d for d in body.get("deleted") or [] if isinstance(d, dict)],
    }


def _decision_node(decision: dict[str, Any], active: bool, pseudo: Any, policy: Any):
    node = pseudo.record(decision, policy)
    node.update(
        {
            "id": f"crowdsec:decision:{decision.get('id')}",
            "node_type": "IntrusionDecision",
            "active": active,
            "epistemic_class": "observation",
        }
    )
    return node


def ingest_decisions(
    new: list[dict[str, Any]],
    deleted: list[dict[str, Any]] | None = None,
    *,
    pseudonymizer: Any | None = None,
    client: Any | None = None,
    graph: str | None = None,
) -> dict[str, int]:
    """Ingest added (active) and deleted (inactive) decisions."""
    from agent_utilities.security.audit_pseudonym import (
        AuditFieldPolicy,
        AuditPseudonymizer,
    )

    pseudo = pseudonymizer or AuditPseudonymizer.from_settings()
    policy = AuditFieldPolicy(**_POLICY)
    batches = ((new or [], True), (deleted or [], False))
    nodes = [
        _decision_node(decision, active, pseudo, policy)
        for decisions, active in batches
        for decision in decisions
        if decision.get("id") is not None
    ]
    if not nodes:
        return {"nodes": 0, "edges": 0}
    return kg_ingest.ingest_entities(nodes, client=client, graph=graph)
