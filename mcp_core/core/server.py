"""
Core MCP server implementation
"""

import logging

# Get logger
logger = logging.getLogger(__name__)

# Create a singleton MCP server instance
_mcp_server = None


def create_mcp_server():
    """Create and configure the MCP server with all tools and resources.

    Returns:
        Configured FastMCP server instance
    """
    # Lazy import to avoid circular dependencies
    from ..prompts.diagram_prompts import register_diagram_prompts
    from ..resources.diagram_resources import register_diagram_resources
    from ..server.fastmcp_wrapper import FastMCP
    from ..tools.diagram_tools import register_diagram_tools
    from .config import MCP_SETTINGS

    # Initialize MCP server
    # Note: stateless_http is configured via the FASTMCP_STATELESS_HTTP env var
    # (passed to run_http_async/http_app, not the constructor)
    logger.info(f"Creating MCP server: {MCP_SETTINGS.server_name}")
    server = FastMCP(MCP_SETTINGS.server_name)

    # Register all tools, resources, and prompts
    tool_names = register_diagram_tools(server)
    resource_names = register_diagram_resources(server)
    prompt_names = register_diagram_prompts(server)

    # Update settings with registered tools and prompts
    MCP_SETTINGS.tools = tool_names
    MCP_SETTINGS.prompts = prompt_names
    MCP_SETTINGS.resources = resource_names

    logger.info(
        "MCP server created with %s tools, %s prompts, and %s resources",
        len(MCP_SETTINGS.tools),
        len(MCP_SETTINGS.prompts),
        len(MCP_SETTINGS.resources),
    )
    return server


def get_mcp_server():
    """Get the singleton MCP server instance.

    Returns:
        FastMCP server instance
    """
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = create_mcp_server()
    return _mcp_server


def main():
    """Entry point for the mcp-server console script (argparse, Rich UI, then start server)."""
    from .cli import run

    run()


def start_server(transport="stdio", host=None, port=None):
    """Start the MCP server with the specified transport.

    Args:
        transport (str): Transport protocol to use ('stdio' or 'http')
        host (str, optional): Host address for HTTP transport
        port (int, optional): Port number for HTTP transport
    """
    server = get_mcp_server()

    if transport == "stdio":
        server.run()
    elif transport == "http":
        if not host or not port:
            raise ValueError("Host and port must be specified for HTTP transport")
        server.run_http(host=host, port=port)
    else:
        raise ValueError(f"Unsupported transport: {transport}")
