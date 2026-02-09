"""
Tests for the core utilities of UML-MCP.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from mcp_core.core.utils import generate_diagram


@pytest.fixture
def mock_kroki_client():
    """Mock the Kroki client for testing."""
    mock_client = MagicMock()
    mock_client.generate_diagram.return_value = {
        "url": "https://kroki.io/plantuml/svg/test_url",
        "content": b"<svg>test content</svg>",
        "playground": "https://playground.example.com",
    }
    with patch("mcp_core.core.utils.get_kroki_client", return_value=mock_client):
        yield mock_client


def test_generate_diagram_success(mock_kroki_client, tmp_path):
    """Test successful diagram generation."""
    # Call generate_diagram with test data
    result = generate_diagram(
        diagram_type="class",
        code="@startuml\nclass Test\n@enduml",
        output_format="svg",
        output_dir=str(tmp_path),
    )

    # Verify result structure
    assert "code" in result
    assert "url" in result
    assert "playground" in result
    assert "local_path" in result

    # Verify mock was called with correct params
    mock_kroki_client.generate_diagram.assert_called_once()
    args, kwargs = mock_kroki_client.generate_diagram.call_args
    assert args[0] == "plantuml"  # Backend for class diagrams
    assert "@startuml" in args[1]  # Code contains correct markup
    assert args[2] == "svg"  # Correct output format


def test_generate_diagram_unsupported_type():
    """Test generating a diagram with unsupported type."""
    result = generate_diagram(
        diagram_type="unsupported_type", code="test code", output_format="svg"
    )

    # Should return error
    assert "error" in result
    assert "Unsupported diagram type" in result["error"]


def test_generate_diagram_exception(mock_kroki_client):
    """Test error handling during diagram generation."""
    # Make mock raise exception
    mock_kroki_client.generate_diagram.side_effect = Exception("Test error")

    # Call function and check result
    result = generate_diagram(
        diagram_type="class", code="@startuml\nclass Test\n@enduml", output_format="svg"
    )

    # Verify error is returned
    assert "error" in result
    assert "Test error" in result["error"]


def test_output_directory_creation(tmp_path):
    """Test that the output directory is created if it doesn't exist."""
    non_existent_dir = os.path.join(tmp_path, "new_dir")

    # Directory shouldn't exist initially
    assert not os.path.exists(non_existent_dir)

    # Call function with non-existent directory
    mock_client = MagicMock()
    mock_client.generate_diagram.return_value = {
        "url": "test_url",
        "content": b"test content",
        "playground": "test_playground",
    }
    with patch("mcp_core.core.utils.get_kroki_client", return_value=mock_client):
        generate_diagram(
            diagram_type="class",
            code="@startuml\nclass Test\n@enduml",
            output_format="svg",
            output_dir=non_existent_dir,
        )

    # Directory should now exist
    assert os.path.exists(non_existent_dir)
