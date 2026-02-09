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

# Register sequential-thinking tool (loads module so @mcp_tool runs)
from . import sequential_thinking  # noqa: F401

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


def _validate_and_generate(
    diagram_type: str,
    code: str,
    output_dir: Optional[str] = None,
    output_format: str = "svg",
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    """Validate inputs and generate diagram. Returns result dict with optional error."""
    try:
        GenerateUMLInput(
            diagram_type=diagram_type,
            code=code,
            output_dir=output_dir,
            output_format=output_format,
            theme=theme,
        )
    except ValidationError as e:
        err_msg = "; ".join(
            f"{err['loc'][0]}: {err['msg']}" for err in e.errors()
        )
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

    return generate_diagram(
        diagram_type, code, output_format, output_dir, theme
    )


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
) -> Dict[str, Any]:
    """Generate a diagram using the specified diagram type.

    Use when: You need to create a diagram of any supported type.
    Don't use when: You need to plan a complex diagram first (use sequentialthinking).

    Args:
        diagram_type: Type of diagram (class, sequence, activity, mermaid, d2, etc.)
        code: The diagram code in the syntax for the chosen type
        output_dir: Directory where to save the generated image (optional)
        output_format: Output format svg, png, or pdf (default: svg)
        theme: PlantUML theme for UML diagrams (e.g. cerulean)

    Returns:
        Dict with code, url, playground, local_path, and optional error
    """
    logger.info(
        f"Called generate_uml tool: type={diagram_type}, code length={len(code)}"
    )
    return _validate_and_generate(
        diagram_type, code, output_dir, output_format, theme
    )


# Class diagram tool
@mcp_tool(
    description="Generate UML class diagram from PlantUML code",
    category="uml",
    example="generate_class_diagram('@startuml\\nclass User\\n@enduml', './output')",
    annotations=ANNOTATIONS_DIAGRAM,
)
def generate_class_diagram(
    code: str,
    output_dir: Optional[str] = None,
    output_format: str = "svg",
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a UML class diagram from PlantUML code.

    Use when: Creating class diagrams showing classes, attributes, relationships.
    Don't use when: You need sequence or activity diagrams (use those tools instead).

    Args:
        code: The PlantUML diagram code
        output_dir: Directory where to save the generated image (optional)
        output_format: svg, png, or pdf (default: svg)
        theme: PlantUML theme (e.g. cerulean)

    Returns:
        Dict with code, url, playground, local_path, and optional error
    """
    logger.info(f"Called generate_class_diagram tool: code length={len(code)}")
    return generate_uml("class", code, output_dir, output_format, theme)


# Sequence diagram tool
@mcp_tool(
    description="Generate UML sequence diagram from PlantUML code",
    category="uml",
    example="generate_sequence_diagram('@startuml\\nAlice -> Bob: hello\\n@enduml')",
    annotations=ANNOTATIONS_DIAGRAM,
)
def generate_sequence_diagram(
    code: str,
    output_dir: Optional[str] = None,
    output_format: str = "svg",
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a UML sequence diagram from PlantUML code.

    Args:
        code: The PlantUML diagram code
        output_dir: Directory where to save the generated image (optional)
        output_format: svg, png, or pdf (default: svg)
        theme: PlantUML theme (optional)

    Returns:
        Dict with code, url, playground, local_path, and optional error
    """
    logger.info(f"Called generate_sequence_diagram tool: code length={len(code)}")
    return generate_uml("sequence", code, output_dir, output_format, theme)


# Activity diagram tool
@mcp_tool(
    description="Generate UML activity diagram from PlantUML code",
    category="uml",
    example="generate_activity_diagram('@startuml\\nstart\\n:do work;\\n@enduml')",
    annotations=ANNOTATIONS_DIAGRAM,
)
def generate_activity_diagram(
    code: str,
    output_dir: Optional[str] = None,
    output_format: str = "svg",
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a UML activity diagram from PlantUML code.

    Args:
        code: The PlantUML diagram code
        output_dir: Directory where to save the generated image (optional)
        output_format: svg, png, or pdf (default: svg)
        theme: PlantUML theme (optional)

    Returns:
        Dict with code, url, playground, local_path, and optional error
    """
    logger.info(f"Called generate_activity_diagram tool: code length={len(code)}")
    return generate_uml("activity", code, output_dir, output_format, theme)


# Use case diagram tool
@mcp_tool(
    description="Generate UML use case diagram from PlantUML code",
    category="uml",
    example="generate_usecase_diagram('@startuml\\nactor User\\n@enduml')",
    annotations=ANNOTATIONS_DIAGRAM,
)
def generate_usecase_diagram(
    code: str,
    output_dir: Optional[str] = None,
    output_format: str = "svg",
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a UML use case diagram from PlantUML code.

    Args:
        code: The PlantUML diagram code
        output_dir: Directory where to save the generated image (optional)
        output_format: svg, png, or pdf (default: svg)
        theme: PlantUML theme (optional)

    Returns:
        Dict with code, url, playground, local_path, and optional error
    """
    logger.info(f"Called generate_usecase_diagram tool: code length={len(code)}")
    return generate_uml("usecase", code, output_dir, output_format, theme)


# State diagram tool
@mcp_tool(
    description="Generate UML state diagram from PlantUML code",
    category="uml",
    example="generate_state_diagram('@startuml\\n[*] --> Idle\\n@enduml')",
    annotations=ANNOTATIONS_DIAGRAM,
)
def generate_state_diagram(
    code: str,
    output_dir: Optional[str] = None,
    output_format: str = "svg",
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a UML state diagram from PlantUML code.

    Args:
        code: The PlantUML diagram code
        output_dir: Directory where to save the generated image (optional)
        output_format: svg, png, or pdf (default: svg)
        theme: PlantUML theme (optional)

    Returns:
        Dict with code, url, playground, local_path, and optional error
    """
    logger.info(f"Called generate_state_diagram tool: code length={len(code)}")
    return generate_uml("state", code, output_dir, output_format, theme)


# Component diagram tool
@mcp_tool(
    description="Generate UML component diagram from PlantUML code",
    category="uml",
    example="generate_component_diagram('@startuml\\n[Component]\\n@enduml')",
    annotations=ANNOTATIONS_DIAGRAM,
)
def generate_component_diagram(
    code: str,
    output_dir: Optional[str] = None,
    output_format: str = "svg",
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a UML component diagram from PlantUML code.

    Args:
        code: The PlantUML diagram code
        output_dir: Directory where to save the generated image (optional)
        output_format: svg, png, or pdf (default: svg)
        theme: PlantUML theme (optional)

    Returns:
        Dict with code, url, playground, local_path, and optional error
    """
    logger.info(f"Called generate_component_diagram tool: code length={len(code)}")
    return generate_uml("component", code, output_dir, output_format, theme)


# Deployment diagram tool
@mcp_tool(
    description="Generate UML deployment diagram from PlantUML code",
    category="uml",
    example="generate_deployment_diagram('@startuml\\nnode n1\\n@enduml')",
    annotations=ANNOTATIONS_DIAGRAM,
)
def generate_deployment_diagram(
    code: str,
    output_dir: Optional[str] = None,
    output_format: str = "svg",
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a UML deployment diagram from PlantUML code.

    Args:
        code: The PlantUML diagram code
        output_dir: Directory where to save the generated image (optional)
        output_format: svg, png, or pdf (default: svg)
        theme: PlantUML theme (optional)

    Returns:
        Dict with code, url, playground, local_path, and optional error
    """
    logger.info(f"Called generate_deployment_diagram tool: code length={len(code)}")
    return generate_uml("deployment", code, output_dir, output_format, theme)


# Object diagram tool
@mcp_tool(
    description="Generate UML object diagram from PlantUML code",
    category="uml",
    example="generate_object_diagram('@startuml\\nobject o1\\n@enduml')",
    annotations=ANNOTATIONS_DIAGRAM,
)
def generate_object_diagram(
    code: str,
    output_dir: Optional[str] = None,
    output_format: str = "svg",
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a UML object diagram from PlantUML code.

    Args:
        code: The PlantUML diagram code
        output_dir: Directory where to save the generated image (optional)
        output_format: svg, png, or pdf (default: svg)
        theme: PlantUML theme (optional)

    Returns:
        Dict with code, url, playground, local_path, and optional error
    """
    logger.info(f"Called generate_object_diagram tool: code length={len(code)}")
    return generate_uml("object", code, output_dir, output_format, theme)


# Mermaid diagram tool
@mcp_tool(
    description="Generate diagrams using Mermaid syntax",
    category="other",
    example="generate_mermaid_diagram('graph TD; A-->B;')",
    annotations=ANNOTATIONS_DIAGRAM,
)
def generate_mermaid_diagram(
    code: str,
    output_dir: Optional[str] = None,
    output_format: str = "svg",
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a diagram using Mermaid syntax.

    Args:
        code: The Mermaid diagram code
        output_dir: Directory where to save the generated image (optional)
        output_format: svg or png (default: svg)
        theme: Ignored for Mermaid (reserved for PlantUML)

    Returns:
        Dict with code, url, playground, local_path, and optional error
    """
    logger.info(f"Called generate_mermaid_diagram tool: code length={len(code)}")
    return generate_uml("mermaid", code, output_dir, output_format, None)


# D2 diagram tool
@mcp_tool(
    description="Generate diagrams using D2 syntax",
    category="other",
    example="generate_d2_diagram('x -> y')",
    annotations=ANNOTATIONS_DIAGRAM,
)
def generate_d2_diagram(
    code: str,
    output_dir: Optional[str] = None,
    output_format: str = "svg",
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a diagram using D2 syntax.

    Args:
        code: The D2 diagram code
        output_dir: Directory where to save the generated image (optional)
        output_format: svg or png (default: svg)
        theme: Ignored for D2 (reserved for PlantUML)

    Returns:
        Dict with code, url, playground, local_path, and optional error
    """
    logger.info(f"Called generate_d2_diagram tool: code length={len(code)}")
    return generate_uml("d2", code, output_dir, output_format, None)


# Graphviz diagram tool
@mcp_tool(
    description="Generate diagrams using Graphviz DOT syntax",
    category="other",
    example="generate_graphviz_diagram('digraph { a -> b; }')",
    annotations=ANNOTATIONS_DIAGRAM,
)
def generate_graphviz_diagram(
    code: str,
    output_dir: Optional[str] = None,
    output_format: str = "svg",
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a diagram using Graphviz DOT syntax.

    Args:
        code: The Graphviz DOT code
        output_dir: Directory where to save the generated image (optional)
        output_format: svg, png, or pdf (default: svg)
        theme: Ignored for Graphviz (reserved for PlantUML)

    Returns:
        Dict with code, url, playground, local_path, and optional error
    """
    logger.info(f"Called generate_graphviz_diagram tool: code length={len(code)}")
    return generate_uml("graphviz", code, output_dir, output_format, None)


# ERD diagram tool
@mcp_tool(
    description="Generate Entity-Relationship diagrams",
    category="database",
    example="generate_erd_diagram('entity E { id int }')",
    annotations=ANNOTATIONS_DIAGRAM,
)
def generate_erd_diagram(
    code: str,
    output_dir: Optional[str] = None,
    output_format: str = "svg",
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate an Entity-Relationship diagram.

    Args:
        code: The ERD diagram code
        output_dir: Directory where to save the generated image (optional)
        output_format: svg, png, or pdf (default: svg)
        theme: Ignored for ERD (reserved for PlantUML)

    Returns:
        Dict with code, url, playground, local_path, and optional error
    """
    logger.info(f"Called generate_erd_diagram tool: code length={len(code)}")
    return generate_uml("erd", code, output_dir, output_format, None)


# BlockDiag diagram tool
@mcp_tool(
    description="Generate simple block diagrams using BlockDiag syntax",
    category="other",
    example="generate_blockdiag_diagram('blockdiag { A -> B; }')",
    annotations=ANNOTATIONS_DIAGRAM,
)
def generate_blockdiag_diagram(
    code: str,
    output_dir: Optional[str] = None,
    output_format: str = "svg",
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a block diagram using BlockDiag syntax.

    Args:
        code: The BlockDiag diagram code
        output_dir: Directory where to save the generated image (optional)
        output_format: svg, png, or pdf (default: svg)
        theme: Ignored for BlockDiag

    Returns:
        Dict with code, url, playground, local_path, and optional error
    """
    logger.info(f"Called generate_blockdiag_diagram tool: code length={len(code)}")
    return generate_uml("blockdiag", code, output_dir, output_format, None)


# BPMN diagram tool
@mcp_tool(
    description="Generate Business Process Model and Notation (BPMN) diagrams",
    category="other",
    example="generate_bpmn_diagram('<bpmn:definitions>...</bpmn:definitions>')",
    annotations=ANNOTATIONS_DIAGRAM,
)
def generate_bpmn_diagram(
    code: str,
    output_dir: Optional[str] = None,
    output_format: str = "svg",
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a BPMN diagram.

    Args:
        code: The BPMN XML diagram code
        output_dir: Directory where to save the generated image (optional)
        output_format: svg only for BPMN (default: svg)
        theme: Ignored for BPMN

    Returns:
        Dict with code, url, playground, local_path, and optional error
    """
    logger.info(f"Called generate_bpmn_diagram tool: code length={len(code)}")
    return generate_uml("bpmn", code, output_dir, output_format, None)


# C4 PlantUML diagram tool
@mcp_tool(
    description="Generate C4 model architecture diagrams using PlantUML",
    category="uml",
    example="generate_c4_diagram('@startuml\\n!include C4_Context.puml\\nPerson(user)\\n@enduml')",
    annotations=ANNOTATIONS_DIAGRAM,
)
def generate_c4_diagram(
    code: str,
    output_dir: Optional[str] = None,
    output_format: str = "svg",
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a C4 architecture diagram using C4-PlantUML.

    Args:
        code: The C4-PlantUML diagram code
        output_dir: Directory where to save the generated image (optional)
        output_format: svg, png, or pdf (default: svg)
        theme: PlantUML theme (optional)

    Returns:
        Dict with code, url, playground, local_path, and optional error
    """
    logger.info(f"Called generate_c4_diagram tool: code length={len(code)}")
    return generate_uml("c4plantuml", code, output_dir, output_format, theme)


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
