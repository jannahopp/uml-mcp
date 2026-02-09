"""
Tests for the FastAPI application.
"""

import json
import os
from unittest.mock import mock_open, patch

import pytest
from fastapi.testclient import TestClient

# Set testing environment variable before importing app
os.environ["TESTING"] = "true"

from app import app  # noqa: E402

# Create test client
client = TestClient(app)


@pytest.fixture
def mock_generate_diagram():
    """Mock the generate_diagram function."""
    with patch("app.generate_diagram") as mock_func:
        # Setup mock response
        mock_func.return_value = {
            "code": "@startuml\nclass Test\n@enduml",
            "url": "https://kroki.io/plantuml/svg/test_url",
            "playground": "https://playground.example.com",
            "local_path": "/tmp/diagrams/test.svg",
        }
        yield mock_func


@pytest.fixture
def mock_plugin_manifest():
    """Mock the plugin manifest file read."""
    manifest_content = {
        "schema_version": "v1",
        "name_for_human": "UML Diagram Generator",
        "description_for_human": "Generate UML diagrams from text",
        "auth": {"type": "none"},
        "api": {"type": "openapi", "url": "https://example.com/openapi.json"},
        "logo_url": "https://example.com/logo.png",
    }

    with patch("builtins.open", mock_open(read_data=json.dumps(manifest_content))):
        yield


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to the UML-MCP API"
    assert "version" in response.json()


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()
    assert "modules_available" in response.json()


def test_generate_diagram_endpoint_success(mock_generate_diagram):
    """Test successful diagram generation."""
    # Test data
    request_data = {
        "lang": "plantuml",
        "type": "class",
        "code": "@startuml\nclass Test\n@enduml",
        "theme": "default",
        "output_format": "svg",
    }

    # Make request
    response = client.post("/generate_diagram", json=request_data)

    # Verify response
    assert response.status_code == 200
    assert "url" in response.json()
    assert "playground" in response.json()

    # Verify mock was called with correct params (app injects !theme when theme is provided)
    mock_generate_diagram.assert_called_once()
    args, kwargs = mock_generate_diagram.call_args
    assert kwargs["diagram_type"] == "class"
    assert (
        "@startuml" in kwargs["code"]
        and "class Test" in kwargs["code"]
        and "@enduml" in kwargs["code"]
    )
    assert "!theme default" in kwargs["code"]
    assert kwargs["output_format"] == "svg"


def test_generate_diagram_endpoint_error(mock_generate_diagram):
    """Test error handling in diagram generation endpoint."""
    # Setup mock to return error
    mock_generate_diagram.return_value = {
        "code": "test code",
        "error": "Test error message",
        "url": None,
        "playground": None,
        "local_path": None,
    }

    # Test data
    request_data = {
        "lang": "plantuml",
        "type": "class",
        "code": "invalid code",
        "theme": "default",
    }

    # Make request
    response = client.post("/generate_diagram", json=request_data)

    # Verify response
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "Test error message" in response.json()["detail"]


def test_plugin_manifest_endpoint(mock_plugin_manifest):
    """Test the plugin manifest endpoint."""
    response = client.get("/.well-known/ai-plugin.json")
    assert response.status_code == 200
    assert "schema_version" in response.json()
    assert "name_for_human" in response.json()


def test_openapi_spec():
    """Test the OpenAPI specification endpoint."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    # OpenAPI spec should contain standard fields
    assert "openapi" in response.json()
    assert "info" in response.json()
    assert "paths" in response.json()
