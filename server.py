#!/usr/bin/env python3
"""
Canonical MCP server entry point for UML diagram generation.

Uses mcp_core (tools, config, Kroki) for consistent diagram generation.
Run with: python server.py [--transport stdio|http] [--host 127.0.0.1] [--port 8000]
Or with FastMCP CLI: fastmcp run server.py / fastmcp run fastmcp.json
"""

from mcp_core.core.server import get_mcp_server, main

# Expose for FastMCP CLI (fastmcp run server.py / fastmcp run fastmcp.json)
mcp = get_mcp_server()

if __name__ == "__main__":
    main()
