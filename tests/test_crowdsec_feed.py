"""EH-410: CrowdSec decisions as :IntrusionDecision nodes; ban targets kept whole."""

from __future__ import annotations

from typing import Any

from agent_utilities.security.audit_pseudonym import AuditPseudonymizer

from caddy_mcp import crowdsec_feed, kg_ingest

PSEUDO = AuditPseudonymizer(b"test-only-audit-key")


def test_new_and_deleted_decisions_are_ingested(monkeypatch):
    written: dict[str, dict[str, Any]] = {}

    def capture(entities, relationships=None, **_kwargs):
        written.update({entity["id"]: entity for entity in entities})
        return {"nodes": len(entities), "edges": 0}

    monkeypatch.setattr(kg_ingest, "ingest_entities", capture)
    ban = {
        "id": 41,
        "origin": "crowdsec",
        "type": "ban",
        "scope": "Ip",
        "value": "203.0.113.77",
        "scenario": "crowdsecurity/http-probing",
        "duration": "3h59m",
        "uuid": "internal",
    }
    gone = {"id": 7, "type": "ban", "scope": "Range", "value": "198.51.100.0/24"}
    res = crowdsec_feed.ingest_decisions([ban], [gone], pseudonymizer=PSEUDO)
    assert res == {"nodes": 2, "edges": 0}
    active = written["crowdsec:decision:41"]
    assert active["node_type"] == "IntrusionDecision" and active["active"] is True
    assert active["value"] == "203.0.113.77", "the ban target is kept whole"
    assert active["scenario"] == "crowdsecurity/http-probing"
    assert "uuid" not in active
    assert written["crowdsec:decision:7"]["active"] is False
    assert crowdsec_feed.ingest_decisions([], None, pseudonymizer=PSEUDO) == {
        "nodes": 0,
        "edges": 0,
    }
