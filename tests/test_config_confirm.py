"""CONN-CADDY-MCP-R002: live-config writes require confirmation, stdio included."""

import asyncio
import json
import socket
import threading
import time

import pytest
from fastmcp import Client

from caddy_mcp.api.api_client_base import ApiClientBase

GATED = (
    "caddy_load_config",
    "caddy_put_config",
    "caddy_patch_config",
    "caddy_put_id",
    "caddy_patch_id",
    "caddy_post_id",
    "caddy_post_config",
    "caddy_set_config",
)
ARGS = {
    "caddy_load_config": {"config": {"apps": {}}},
    "caddy_put_config": {"path": "apps/http/servers/x", "config": {"a": 1}},
    "caddy_patch_config": {"path": "apps/http/servers/x", "config": {"a": 2}},
    "caddy_put_id": {"id_path": "site-x", "config": {"a": 1}},
    "caddy_patch_id": {"id_path": "site-x", "config": {"a": 2}},
    "caddy_post_id": {"id_path": "site-x/routes", "config": {"a": 3}},
    "caddy_post_config": {"path": "apps/http/servers/x/routes", "config": {"a": 4}},
    "caddy_set_config": {"path": "apps/http/servers/x/routes", "config": {"a": 5}},
}


@pytest.fixture
def upstream(monkeypatch):
    calls = []

    def fake(self, method, endpoint, **kw):
        calls.append((method, endpoint))
        return {"status": "success"}

    monkeypatch.setattr(ApiClientBase, "request", fake)
    return calls


def _server(args):
    from scion_sdk._connector_serve import build_server

    return build_server("caddy_mcp", command_args=args)[1]


def _payload(result):
    return result.structured_content or json.loads(result.content[0].text)


@pytest.mark.parametrize("name", GATED)
def test_gated_tools_are_destructive_and_take_confirm(name):
    tool = {t.name: t for t in asyncio.run(_server([]).list_tools())}[name]
    assert "confirm" in tool.parameters["properties"]
    assert tool.annotations.destructive_hint is True


@pytest.mark.parametrize("name", GATED)
def test_stdio_no_auth_refuses_without_confirm_and_never_calls_caddy(name, upstream):
    """No elicitation-capable client, no auth: a typed refusal, not a hang."""

    async def run():
        async with Client(_server([])) as c:
            return await asyncio.wait_for(c.call_tool(name, ARGS[name]), 20)

    out = _payload(asyncio.run(run()))
    assert out["cancelled"] is True
    assert "confirm=true" in out["reason"]
    assert upstream == []


@pytest.mark.parametrize("name", GATED)
def test_stdio_no_auth_succeeds_with_confirm_true(name, upstream):
    async def run():
        async with Client(_server([])) as c:
            return await asyncio.wait_for(
                c.call_tool(name, {**ARGS[name], "confirm": True}), 20
            )

    out = _payload(asyncio.run(run()))
    assert out.get("cancelled") is not True
    assert len(upstream) == 1


def _free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture
def http_url():
    port = _free_port()
    mcp = _server(
        ["--transport", "streamable-http", "--host", "127.0.0.1",
         "--port", str(port), "--auth-type", "none"]
    )  # fmt: skip
    threading.Thread(
        target=lambda: asyncio.run(
            mcp.run_http_async(host="127.0.0.1", port=port, show_banner=False)
        ),
        daemon=True,
    ).start()
    for _ in range(100):
        try:
            socket.create_connection(("127.0.0.1", port), 0.2).close()
            break
        except OSError:
            time.sleep(0.1)
    return f"http://127.0.0.1:{port}/mcp"


@pytest.mark.parametrize("name", GATED)
def test_http_refuses_without_confirm_then_succeeds_with_it(name, http_url, upstream):
    async def run():
        async with Client(http_url) as c:
            refused = await asyncio.wait_for(c.call_tool(name, ARGS[name]), 20)
            assert upstream == []
            done = await asyncio.wait_for(
                c.call_tool(name, {**ARGS[name], "confirm": True}), 20
            )
            return refused, done

    refused, done = asyncio.run(run())
    assert _payload(refused)["cancelled"] is True
    assert _payload(done).get("cancelled") is not True
    assert len(upstream) == 1
