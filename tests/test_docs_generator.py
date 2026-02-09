"""
Tests for mcp_core.api.docs_generator.
"""

import json
from unittest.mock import patch

import pytest

from mcp_core.api.docs_generator import (
    generate_api_docs,
    get_resource_description,
    get_resource_schema,
    save_api_docs,
)


@pytest.fixture
def mock_mcp_settings():
    """Patch MCP_SETTINGS for docs_generator tests."""
    with patch("mcp_core.api.docs_generator.MCP_SETTINGS") as m:
        m.server_name = "Test UML Server"
        m.description = "Test description"
        m.version = "1.0.0-test"
        yield m


class TestGenerateApiDocs:
    """Tests for generate_api_docs()."""

    def test_returns_openapi_structure(self, mock_mcp_settings):
        """generate_api_docs returns dict with openapi, info, paths, components."""
        result = generate_api_docs()
        assert result["openapi"] == "3.0.0"
        assert "info" in result
        assert result["info"]["title"] == "Test UML Server"
        assert result["info"]["description"] == "Test description"
        assert result["info"]["version"] == "1.0.0-test"
        assert "paths" in result
        assert "components" in result
        assert "schemas" in result["components"]

    def test_schemas_contain_expected_keys(self, mock_mcp_settings):
        """components.schemas has DiagramRequest, UMLDiagramRequest, DiagramResponse."""
        result = generate_api_docs()
        schemas = result["components"]["schemas"]
        assert "DiagramRequest" in schemas
        assert "UMLDiagramRequest" in schemas
        assert "DiagramResponse" in schemas

    def test_paths_contain_tool_endpoints(self, mock_mcp_settings):
        """paths include generate-uml and per-type generate-* endpoints."""
        result = generate_api_docs()
        paths = result["paths"]
        assert "/generate-uml" in paths
        assert "/generate-class-diagram" in paths
        assert "/generate-sequence-diagram" in paths


@pytest.mark.parametrize(
    "resource_path,expected_substring",
    [
        ("uml://types", "supported UML diagram types"),
        ("uml://templates", "Template code"),
        ("uml://examples", "Example UML diagrams"),
        ("uml://formats", "output formats"),
        ("uml://server-info", "Server configuration"),
        ("uml://unknown", "Resource for uml://unknown"),
    ],
)
def test_get_resource_description(resource_path, expected_substring):
    """get_resource_description returns expected string for known and unknown paths."""
    result = get_resource_description(resource_path)
    assert isinstance(result, str)
    assert expected_substring in result


class TestGetResourceSchema:
    """Tests for get_resource_schema()."""

    def test_uml_types_schema_has_types_and_descriptions(self):
        """uml://types returns schema with types array and descriptions."""
        result = get_resource_schema("uml://types")
        assert result["type"] == "object"
        assert "properties" in result
        assert "types" in result["properties"]
        assert "descriptions" in result["properties"]

    def test_uml_templates_schema_has_templates(self):
        """uml://templates returns schema with templates property."""
        result = get_resource_schema("uml://templates")
        assert result["type"] == "object"
        assert "properties" in result
        assert "templates" in result["properties"]

    def test_uml_examples_schema_has_examples(self):
        """uml://examples returns schema with examples property."""
        result = get_resource_schema("uml://examples")
        assert result["type"] == "object"
        assert "properties" in result
        assert "examples" in result["properties"]

    def test_unknown_path_returns_generic_object(self):
        """Unknown resource_path returns generic object schema."""
        result = get_resource_schema("uml://other")
        assert result == {"type": "object"}


class TestSaveApiDocs:
    """Tests for save_api_docs()."""

    def test_save_api_docs_creates_file(self, mock_mcp_settings, tmp_path):
        """save_api_docs writes openapi.json to output_dir."""
        out_dir = str(tmp_path)
        path = save_api_docs(output_dir=out_dir)
        assert path.replace("\\", "/").endswith("openapi.json")
        assert (tmp_path / "openapi.json").exists()

    def test_saved_file_is_valid_json_with_expected_keys(
        self, mock_mcp_settings, tmp_path
    ):
        """Saved JSON has openapi, info, paths, components."""
        save_api_docs(output_dir=str(tmp_path))
        with open(tmp_path / "openapi.json") as f:
            data = json.load(f)
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data
        assert "components" in data
