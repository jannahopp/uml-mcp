"""
Unit tests for diagram tool functions
"""

from unittest.mock import MagicMock, patch

import pytest

from mcp_core.tools.diagram_tools import (
    generate_activity_diagram,
    generate_blockdiag_diagram,
    generate_bpmn_diagram,
    generate_c4_diagram,
    generate_class_diagram,
    generate_component_diagram,
    generate_d2_diagram,
    generate_deployment_diagram,
    generate_erd_diagram,
    generate_graphviz_diagram,
    generate_mermaid_diagram,
    generate_object_diagram,
    generate_sequence_diagram,
    generate_state_diagram,
    generate_uml,
    generate_usecase_diagram,
    register_diagram_tools,
)
from mcp_core.tools.sequential_thinking import sequentialthinking

# Parametrized data: (tool_function, diagram_type, sample_code)
GENERATE_TOOL_CASES = [
    (generate_sequence_diagram, "sequence", "@startuml\nAlice -> Bob: hello\n@enduml"),
    (generate_activity_diagram, "activity", "@startuml\nstart\n:do work;\n@enduml"),
    (generate_usecase_diagram, "usecase", "@startuml\nactor User\n@enduml"),
    (generate_state_diagram, "state", "@startuml\n[*] --> Idle\n@enduml"),
    (generate_component_diagram, "component", "@startuml\n[Component]\n@enduml"),
    (generate_deployment_diagram, "deployment", "@startuml\nnode n1\n@enduml"),
    (generate_object_diagram, "object", "@startuml\nobject o1\n@enduml"),
    (generate_mermaid_diagram, "mermaid", "graph TD;\nA-->B;"),
    (generate_d2_diagram, "d2", "x -> y"),
    (generate_graphviz_diagram, "graphviz", "digraph { a -> b; }"),
    (generate_erd_diagram, "erd", "entity E { id int }"),
    (generate_blockdiag_diagram, "blockdiag", "blockdiag { A -> B; }"),
    (generate_bpmn_diagram, "bpmn", '<?xml version="1.0"?><bpmn:definitions/>'),
    (generate_c4_diagram, "c4plantuml", "@startuml\n!include C4_Context.puml\nPerson(user)\n@enduml"),
]


class TestDiagramTools:
    """Test suite for diagram tools functionality"""

    @pytest.fixture
    def mock_mcp_server(self):
        """Fixture to create a mock MCP server"""
        server = MagicMock()
        server.tool = MagicMock()
        return server

    def test_register_diagram_tools(self, mock_mcp_server):
        """Test that diagram tools are registered correctly"""
        # Call the register function
        register_diagram_tools(mock_mcp_server)

        # Verify that tool registration was called for each diagram type
        expected_tools = [
            "generate_uml",
            "generate_class_diagram",
            "generate_sequence_diagram",
            "generate_activity_diagram",
            "generate_usecase_diagram",
            "generate_state_diagram",
            "generate_component_diagram",
            "generate_deployment_diagram",
            "generate_object_diagram",
            "generate_mermaid_diagram",
            "generate_d2_diagram",
            "generate_graphviz_diagram",
            "generate_erd_diagram",
            "generate_blockdiag_diagram",
            "generate_bpmn_diagram",
            "generate_c4_diagram",
            "sequentialthinking",
        ]

        # Check that each expected tool was registered (tool is called with name=... or as decorator)
        for tool_name in expected_tools:
            matching_calls = [
                c
                for c in mock_mcp_server.tool.call_args_list
                if (c[0] and c[0][0] == tool_name)
                or (c[1] and c[1].get("name") == tool_name)
            ]
            assert len(matching_calls) > 0, f"Tool {tool_name} was not registered"

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
    def test_generate_class_diagram_tool_calls_generate_uml(
        self, mock_generate_diagram
    ):
        """Test that generate_class_diagram tool invokes diagram generation with class type."""
        mock_generate_diagram.return_value = {
            "code": "@startuml\nclass A\n@enduml",
            "url": "https://kroki.io/plantuml/svg/def",
            "playground": "https://www.plantuml.com/plantuml/uml/~1abc",
        }
        result = generate_class_diagram(code="@startuml\nclass A\n@enduml")
        assert "url" in result
        assert result["code"] == "@startuml\nclass A\n@enduml"
        mock_generate_diagram.assert_called_once()
        call_args = mock_generate_diagram.call_args[0]
        assert call_args[0] == "class"

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

    @pytest.mark.parametrize("tool_func,diagram_type,sample_code", GENERATE_TOOL_CASES)
    @patch("mcp_core.tools.diagram_tools.generate_diagram")
    def test_generate_tool_calls_generate_uml_with_correct_type(
        self, mock_generate_diagram, tool_func, diagram_type, sample_code
    ):
        """Each generate_* tool calls generate_uml with correct diagram_type and returns url, code, playground."""
        mock_generate_diagram.return_value = {
            "code": sample_code,
            "url": f"https://kroki.io/{diagram_type}/svg/abc",
            "playground": "https://example.com/playground",
            "local_path": "/tmp/out/diagram.svg",
        }
        result = tool_func(code=sample_code, output_dir="/tmp/out")
        assert "url" in result
        assert "code" in result
        assert result.get("playground") is not None
        mock_generate_diagram.assert_called_once()
        call_args = mock_generate_diagram.call_args[0]
        assert call_args[0] == diagram_type
        assert call_args[1] == sample_code
        assert call_args[2] == "svg"
        assert call_args[3] == "/tmp/out"
        assert call_args[4] is None  # theme

    def test_sequentialthinking_returns_expected_shape(self):
        """sequentialthinking returns thoughtNumber, totalThoughts,
        nextThoughtNeeded, branches, thoughtHistoryLength."""
        result = sequentialthinking(
            thought="Choose class diagram for the domain model.",
            nextThoughtNeeded=True,
            thoughtNumber=1,
            totalThoughts=3,
        )
        assert "thoughtNumber" in result
        assert "totalThoughts" in result
        assert "nextThoughtNeeded" in result
        assert "branches" in result
        assert "thoughtHistoryLength" in result
        assert result["thoughtNumber"] == 1
        assert result["totalThoughts"] == 3
        assert result["nextThoughtNeeded"] is True
        assert result["thoughtHistoryLength"] == 1
        # Second thought
        result2 = sequentialthinking(
            thought="Verify: class diagram is correct.",
            nextThoughtNeeded=False,
            thoughtNumber=2,
            totalThoughts=3,
        )
        assert result2["thoughtHistoryLength"] == 2
        assert result2["nextThoughtNeeded"] is False

    # @patch("mcp.tools.diagram_tools.generate_diagram")
    # def test_generate_uml_tool(self, mock_generate_diagram, mock_mcp_server):
    #     """Test that the generate_uml tool works correctly"""
    #     # Register tools
    #     register_diagram_tools(mock_mcp_server)

    #     # Find the generate_uml tool function
    #     generate_uml_call = next(
    #         call for call in mock_mcp_server.tool.call_args_list
    #         if len(call[0]) > 0 and call[0][0] == "generate_uml"
    #     )

    #     # Get the tool function (second positional argument)
    #     generate_uml_func = generate_uml_call[0][1]

    #     # Setup mock return value
    #     mock_generate_diagram.return_value = {
    #         "code": "test code",
    #         "url": "test url",
    #         "playground": "test playground",
    #         "local_path": "test local path"
    #     }

    #     # Call the tool function
    #     result = generate_uml_func(
    #         diagram_type="class",
    #         code="@startuml\nclass Test\n@enduml",
    #         output_dir="/tmp"
    #     )

    #     # Verify mock was called with correct parameters
    #     mock_generate_diagram.assert_called_once_with(
    #         diagram_type="class",
    #         code="@startuml\nclass Test\n@enduml",
    #         output_format="svg",  # Default format
    #         output_dir="/tmp"
    #     )

    #     # Verify result
    #     assert result == mock_generate_diagram.return_value
