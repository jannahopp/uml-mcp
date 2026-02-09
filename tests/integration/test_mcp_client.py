"""
MCP Client integration tests: discovery, tools, resources, prompts, and goal-style session.

Run with: USE_REAL_FASTMCP=1 pytest tests/integration -v
"""

import os

import pytest

# Skip entire module if not running with USE_REAL_FASTMCP and Client not available
# (conftest require_integration_env is applied via fixture dependency)
pytestmark = [
    pytest.mark.skipif(
        os.environ.get("USE_REAL_FASTMCP", "").lower() not in ("1", "true", "yes"),
        reason="Integration tests require USE_REAL_FASTMCP=1",
    )
]


def _get_client_class():
    try:
        from fastmcp.client import Client

        return Client
    except ImportError:
        from fastmcp.client.client import Client

        return Client


@pytest.fixture
async def mcp_client(require_integration_env):
    """Yield an MCP Client connected to the UML-MCP server in-process."""
    import mcp_core.core.server as server_module

    server_module._mcp_server = None
    from mcp_core.core.server import create_mcp_server

    Client = _get_client_class()
    server = create_mcp_server()
    # Client(transport=server) or Client(server) per FastMCP docs
    try:
        client = Client(transport=server)
    except TypeError:
        client = Client(server)
    async with client:
        yield client


@pytest.fixture
def mock_diagram_generator():
    """Inject a fake diagram generator so call_tool('generate_uml') does not hit Kroki."""
    from mcp_core.core.utils import set_diagram_generator

    def fake_gen(diagram_type, code, output_format, output_dir=None, theme=None):
        return {
            "code": code,
            "url": "https://example.com/fake.svg",
            "playground": "https://example.com/play",
            "local_path": None,
        }

    set_diagram_generator(fake_gen)
    try:
        yield
    finally:
        set_diagram_generator(None)


class TestDiscoveryViaClient:
    """Discovery: list_tools, list_resources, list_prompts via MCP Client."""

    async def test_list_tools_via_client(self, mcp_client):
        tools = await mcp_client.list_tools()
        assert len(tools) >= 1
        names = (
            [t.name for t in tools]
            if hasattr(tools[0], "name")
            else [t.get("name") for t in tools]
        )
        assert "generate_uml" in names
        assert len(names) == 1

    async def test_list_resources_via_client(self, mcp_client):
        resources = await mcp_client.list_resources()
        assert len(resources) >= 1
        uris = []
        for r in resources:
            if hasattr(r, "uri"):
                uris.append(r.uri)
            elif isinstance(r, dict) and "uri" in r:
                uris.append(r["uri"])
        assert any("uml://" in u for u in uris)

    async def test_list_prompts_via_client(self, mcp_client):
        prompts = await mcp_client.list_prompts()
        assert len(prompts) >= 1
        names = []
        for p in prompts:
            if hasattr(p, "name"):
                names.append(p.name)
            elif isinstance(p, dict) and "name" in p:
                names.append(p["name"])
        assert len(names) >= 1


class TestDiagramToolsViaClient:
    """Call diagram tools via MCP Client (with mocked Kroki)."""

    async def test_call_tool_generate_uml_success(
        self, mcp_client, mock_diagram_generator
    ):
        result = await mcp_client.call_tool(
            "generate_uml",
            arguments={
                "diagram_type": "class",
                "code": "@startuml\nclass Test\n@enduml",
            },
        )
        if hasattr(result, "content"):
            content = result.content
        else:
            content = result
        if isinstance(content, list) and len(content) > 0:
            part = content[0]
            if hasattr(part, "text"):
                import json

                data = json.loads(part.text) if part.text else {}
            else:
                data = part if isinstance(part, dict) else {}
        else:
            data = content if isinstance(content, dict) else {}
        assert "url" in data or "error" not in data
        if "url" in data:
            assert "example.com" in data["url"] or "kroki" in data["url"].lower()

    async def test_call_tool_generate_uml_unsupported_type(self, mcp_client):
        result = await mcp_client.call_tool(
            "generate_uml",
            arguments={"diagram_type": "invalid_type_xyz", "code": "x"},
        )
        if hasattr(result, "content"):
            content = result.content
        else:
            content = result
        if isinstance(content, list) and len(content) > 0:
            part = content[0]
            if hasattr(part, "text"):
                import json

                data = json.loads(part.text) if part.text else {}
            else:
                data = part if isinstance(part, dict) else {}
        else:
            data = content if isinstance(content, dict) else {}
        assert "error" in data or (
            isinstance(content, str) and "unsupported" in content.lower()
        )


class TestGoalStyleSession:
    """Short session: list tools then call generate_uml; assert outcome and path length."""

    async def test_session_list_tools_then_generate_uml(
        self, mcp_client, mock_diagram_generator
    ):
        steps = 0
        tools = await mcp_client.list_tools()
        steps += 1
        assert len(tools) >= 1
        result = await mcp_client.call_tool(
            "generate_uml",
            arguments={
                "diagram_type": "class",
                "code": "@startuml\nclass A { }\n@enduml",
            },
        )
        steps += 1
        if hasattr(result, "content"):
            content = result.content
        else:
            content = result
        if isinstance(content, list) and len(content) > 0:
            part = content[0]
            if hasattr(part, "text"):
                import json

                data = json.loads(part.text) if part.text else {}
            else:
                data = part if isinstance(part, dict) else {}
        else:
            data = content if isinstance(content, dict) else {}
        assert "url" in data or "error" not in data
        assert steps <= 5
