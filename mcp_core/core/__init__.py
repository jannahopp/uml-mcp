"""
MCP Core module initialization.
This ensures the mcp.core module is properly recognized.
"""

from .config import MCP_SETTINGS
from .server import create_mcp_server, get_mcp_server, start_server
from .utils import generate_diagram

__all__ = [
    "MCP_SETTINGS",
    "create_mcp_server",
    "get_mcp_server",
    "start_server",
    "generate_diagram",
]
