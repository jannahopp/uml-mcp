"""
MCP prompts for diagram generation
"""

from .diagram_prompts import (
    activity_diagram_prompt,
    class_diagram_prompt,
    get_prompt_registry,
    mcp_prompt,
    sequence_diagram_prompt,
    uml_diagram_prompt,
    usecase_diagram_prompt,
)

__all__ = [
    "uml_diagram_prompt",
    "class_diagram_prompt",
    "sequence_diagram_prompt",
    "activity_diagram_prompt",
    "usecase_diagram_prompt",
    "mcp_prompt",
    "get_prompt_registry",
]
