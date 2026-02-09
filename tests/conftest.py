"""
Pytest configuration and fixtures for UML-MCP tests.

Ensures deterministic test environment (e.g. mock FastMCP when TESTING=1).
"""

import os

# Set TESTING before any mcp_core imports; fastmcp_wrapper decides mock vs real at import time
os.environ.setdefault("TESTING", "1")

import pytest


@pytest.fixture(autouse=True)
def _testing_env(monkeypatch):
    """Use mock FastMCP and avoid real I/O in tests."""
    monkeypatch.setenv("TESTING", "1")


@pytest.fixture
def reset_mcp_server_singleton():
    """Reset the MCP server singleton so create_mcp_server() runs fresh."""
    import mcp_core.core.server as server_module

    old = server_module._mcp_server
    server_module._mcp_server = None
    try:
        yield
    finally:
        server_module._mcp_server = old
