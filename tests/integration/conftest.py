"""
Conftest for MCP Client integration tests.

Run with: USE_REAL_FASTMCP=1 pytest tests/integration -v

These tests use the real FastMCP package and an in-process Client(server) transport.
"""

import os

import pytest


def _use_real_fastmcp():
    return os.environ.get("USE_REAL_FASTMCP", "").lower() in ("1", "true", "yes")


def _client_importable():
    try:
        from fastmcp.client import Client  # noqa: F401

        return True
    except ImportError:
        try:
            from fastmcp.client.client import Client  # noqa: F401

            return True
        except ImportError:
            return False


@pytest.fixture(scope="module")
def require_integration_env():
    """Skip entire module if integration test env is not set."""
    if not _use_real_fastmcp():
        pytest.skip(
            "Integration tests require USE_REAL_FASTMCP=1. "
            "Run: USE_REAL_FASTMCP=1 pytest tests/integration -v",
            allow_module_level=True,
        )
    if not _client_importable():
        pytest.skip(
            "FastMCP Client not importable (fastmcp.client.Client). "
            "Integration tests require a fastmcp version with Client support.",
            allow_module_level=True,
        )
