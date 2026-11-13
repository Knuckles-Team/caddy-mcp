"""Each competency recording is certified against its access contract."""

import asyncio
import json
from pathlib import Path
from unittest.mock import patch

import pytest
from fastmcp import Client
from scion_sdk.connector import build_server
from scion_sdk.access_contract import parse_access_contracts

from caddy_mcp.api_client import Api

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.spec("CONN-CADDY-MCP-CONNECTOR-CONTENT-R002")
def test_competency_contracts_certified():
    contracts = parse_access_contracts(
        (ROOT / "caddy_mcp/ontology/access_contracts.ttl").read_text()
    )
    assert [c.entity for c in contracts] == ["route"]
    (contract,) = contracts
    assert contract.access_kind == "mcp_tool"
    assert contract.operation == "caddy_get_reverse_proxy_upstreams"
    recording = json.loads((ROOT / "tests/recordings/route.json").read_text())

    async def call():
        mcp = build_server("caddy_mcp", command_args=[])[1]
        with patch.object(Api, "get_reverse_proxy_upstreams", return_value=recording):
            async with Client(mcp) as client:
                return await client.call_tool(
                    contract.operation, {}, raise_on_error=False
                )

    result = asyncio.run(call())
    assert not result.is_error
    rows = json.loads(result.content[0].text)
    assert rows == recording
    assert all(field in rows[0] for _, field in contract.predicates)
    assert contract.key_field in rows[0]
    ontology = (ROOT / "caddy_mcp/ontology/caddy.ttl").read_text()
    for prop, _ in contract.predicates:
        assert f":{prop.rsplit('#', 1)[-1]} a owl:DatatypeProperty" in ontology
