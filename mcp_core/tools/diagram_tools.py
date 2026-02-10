"""
MCP tools for diagram generation using the decorator pattern
"""

import logging
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from mcp_core.server.fastmcp_wrapper import FastMCP

from ..core.config import MCP_SETTINGS

# Import core utilities
from ..core.utils import generate_diagram

# Import the tool decorator system
from .tool_decorator import get_tool_registry, mcp_tool, register_tools_with_server
from .schemas import GenerateUMLInput

logger = logging.getLogger(__name__)

# MCP tool annotations per best practices (diagram tools call Kroki, may write files)
ANNOTATIONS_DIAGRAM = {
    "readOnlyHint": False,  # May write files when output_dir provided
    "destructiveHint": False,
    "idempotentHint": True,  # Same inputs produce same diagram via Kroki
    "openWorldHint": True,  # Calls external Kroki service for rendering
}

ANNOTATIONS_URL_ONLY = {
    "readOnlyHint": True,  # No file I/O; returns URL and optional base64
    "destructiveHint": False,
    "idempotentHint": True,
    "openWorldHint": True,
}


def _validate_and_generate(
    diagram_type: str,
    code: str,
    output_dir: Optional[str] = None,
    output_format: str = "svg",
    theme: Optional[str] = None,
    scale: float = 1.0,
) -> Dict[str, Any]:
    """Validate inputs and generate diagram. Returns result dict with optional error."""
    try:
        GenerateUMLInput(
            diagram_type=diagram_type,
            code=code,
            output_dir=output_dir,
            output_format=output_format,
            theme=theme,
            scale=scale,
        )
    except ValidationError as e:
        parts = []
        for err in e.errors():
            loc = err.get("loc", ())
            name = loc[0] if loc else "input"
            parts.append(f"{name}: {err['msg']}")
        err_msg = "; ".join(parts)
        return {
            "code": code,
            "url": None,
            "playground": None,
            "local_path": None,
            "error": f"Validation error: {err_msg}",
        }

    valid_types = getattr(MCP_SETTINGS, "diagram_types", {})
    if not valid_types:
        valid_types = {"class": "Class diagram", "sequence": "Sequence diagram"}

    if diagram_type.lower() not in valid_types:
        error_msg = (
            f"Unsupported diagram type: {diagram_type}. Use uml://types resource "
            "for valid types."
        )
        logger.error(error_msg)
        return {
            "code": code,
            "url": None,
            "playground": None,
            "local_path": None,
            "error": error_msg,
        }

    return generate_diagram(diagram_type, code, output_format, output_dir, theme, scale)


# Main UML generation tool
@mcp_tool(
    description="Generate any UML or diagram by type (class, sequence, mermaid, d2, etc.)",
    category="uml",
    example="generate_uml('class', '@startuml\\nclass User\\n@enduml', './output')",
    annotations=ANNOTATIONS_DIAGRAM,
)
def generate_uml(
    diagram_type: str,
    code: str,
    output_dir: Optional[str] = None,
    output_format: str = "svg",
    theme: Optional[str] = None,
    scale: float = 1.0,
) -> Dict[str, Any]:
    """Generate a diagram using the specified diagram type.

    Use when you need a diagram of any supported type. For complex diagrams the
    default prompt guides planning first (type, elements, relationships), then
    you call this tool with the final code.

    Args:
        diagram_type: Type of diagram (class, sequence, activity, mermaid, d2, etc.)
        code: Diagram code in the syntax for the chosen type
        output_dir: Directory to save the image (optional). Omit for url/playground/content_base64 only.
        output_format: svg, png, pdf, jpeg, txt, or base64 (default: svg). See uml://formats per type.
        theme: PlantUML theme for UML diagrams (e.g. cerulean)
        scale: Scale factor for SVG only (default 1.0, min 0.1). Ignored for other formats.

    Returns:
        Dict with code, url, playground; local_path when output_dir set; content_base64 when not saving; or error.
    """
    logger.info(
        f"Called generate_uml tool: type={diagram_type}, code length={len(code)}"
    )
    return _validate_and_generate(
        diagram_type, code, output_dir, output_format, theme, scale
    )


@mcp_tool(
    description="Get the Kroki URL (and optional base64 image) for a diagram without saving to disk.",
    category="uml",
    example="generate_diagram_url('mermaid', 'graph TD; A-->B;')",
    annotations=ANNOTATIONS_URL_ONLY,
)
def generate_diagram_url(
    diagram_type: str,
    code: str,
    output_format: str = "svg",
    theme: Optional[str] = None,
    scale: float = 1.0,
) -> Dict[str, Any]:
    """Return the diagram URL and optional base64 image; no file is written.

    Use when you only need a link or in-memory image (e.g. serverless, read-only FS).
    To save to disk, use generate_uml with output_dir.

    Args:
        diagram_type: Type of diagram (class, sequence, mermaid, d2, etc.)
        code: Diagram code in the syntax for the chosen type
        output_format: svg, png, pdf, jpeg, etc. (default: svg). See uml://formats per type.
        theme: PlantUML theme for PlantUML diagram types (e.g. cerulean)
        scale: Scale factor for SVG only (default 1.0, min 0.1). Ignored for other formats.

    Returns:
        Dict with code, url, playground, content_base64 on success; or error.
    """
    logger.info(
        f"Called generate_diagram_url tool: type={diagram_type}, code length={len(code)}"
    )
    return _validate_and_generate(diagram_type, code, None, output_format, theme, scale)


def register_diagram_tools(server: FastMCP) -> List[str]:
    """
    Register all diagram generation tools with the MCP server

    Args:
        server: The MCP server instance

    Returns:
        List of registered tool names
    """
    logger.info("Registering diagram tools")

    # Register all tools that were decorated with @mcp_tool
    registered_tools = register_tools_with_server(server)

    # Store registered tools in MCP_SETTINGS.tools (which is a standard attribute)
    MCP_SETTINGS.tools = registered_tools

    logger.info(f"Registered {len(registered_tools)} diagram tools successfully")
    logger.debug(f"Registered tools: {registered_tools}")

    return registered_tools


def get_tool_info() -> Dict[str, Dict[str, Any]]:
    """
    Get information about all registered tools

    Returns:
        Dictionary mapping tool names to their information
    """
    return get_tool_registry()
