#!/usr/bin/env python3
"""
Canonical MCP server entry point for UML diagram generation.

Uses mcp_core (tools, config, Kroki) for consistent diagram generation.
Run with: python server.py [--transport stdio|http] [--host 127.0.0.1] [--port 8000]
"""

from mcp_core.core.server import main

if __name__ == "__main__":
    main()
