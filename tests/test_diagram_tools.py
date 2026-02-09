"""
Unit tests for diagram tool functions
"""

from unittest.mock import MagicMock, patch

import pytest

from mcp_core.tools.diagram_tools import (
    generate_uml,
    register_diagram_tools,
)


class TestDiagramTools:
    """Test suite for diagram tools functionality"""

    @pytest.fixture
    def mock_mcp_server(self):
        """Fixture to create a mock MCP server"""
        server = MagicMock()
        server.tool = MagicMock()
        return server

    def test_register_diagram_tools(self, mock_mcp_server):
        """Test that diagram tools are registered correctly (only generate_uml)."""
        register_diagram_tools(mock_mcp_server)

        expected_tools = ["generate_uml"]

        for tool_name in expected_tools:
            matching_calls = [
                c
                for c in mock_mcp_server.tool.call_args_list
                if (c[0] and c[0][0] == tool_name)
                or (c[1] and c[1].get("name") == tool_name)
            ]
            assert len(matching_calls) > 0, f"Tool {tool_name} was not registered"

        assert mock_mcp_server.tool.call_count == len(expected_tools)

    @patch("mcp_core.tools.diagram_tools.generate_diagram")
    def test_generate_uml_tool_returns_structure(self, mock_generate_diagram):
        """Test that generate_uml tool returns url, code, playground, and optional local_path."""
        mock_generate_diagram.return_value = {
            "code": "@startuml\nclass Test\n@enduml",
            "url": "https://kroki.io/plantuml/svg/abc123",
            "playground": "https://www.plantuml.com/plantuml/uml/~1xyz",
            "local_path": "/tmp/out/class_123.svg",
        }
        result = generate_uml(
            diagram_type="class",
            code="@startuml\nclass Test\n@enduml",
            output_dir="/tmp/out",
        )
        assert "url" in result
        assert "code" in result
        assert result.get("playground") is not None
        assert result.get("local_path") is not None
        mock_generate_diagram.assert_called_once_with(
            "class", "@startuml\nclass Test\n@enduml", "svg", "/tmp/out", None
        )

    @patch("mcp_core.tools.diagram_tools.generate_diagram")
    def test_generate_uml_unsupported_diagram_type_returns_error(
        self, mock_generate_diagram
    ):
        """generate_uml with unsupported diagram type returns error dict and does not call generate_diagram."""
        result = generate_uml(
            diagram_type="invalid_type",
            code="some code",
        )
        assert "error" in result
        assert "Unsupported diagram type" in result["error"]
        assert "invalid_type" in result["error"]
        mock_generate_diagram.assert_not_called()

    @patch("mcp_core.tools.diagram_tools.generate_diagram")
    def test_generate_uml_with_different_types(self, mock_generate_diagram):
        """generate_uml accepts all diagram types via diagram_type argument."""
        mock_generate_diagram.return_value = {
            "code": "sample",
            "url": "https://example.com/svg/abc",
            "playground": "https://example.com/playground",
            "local_path": "/tmp/out/diagram.svg",
        }
        for diagram_type in ("sequence", "class", "mermaid", "d2", "bpmn"):
            result = generate_uml(
                diagram_type=diagram_type,
                code="sample code",
                output_dir="/tmp/out",
            )
            assert "url" in result
            assert result["code"] == "sample"
            call_args = mock_generate_diagram.call_args[0]
            assert call_args[0] == diagram_type
