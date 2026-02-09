"""
Utility functions for MCP server.

Logging is configured only by the CLI entrypoint (mcp_core.core.cli).
Kroki client is lazy-loaded for testability.
"""

import datetime
import logging
import os
from typing import Any, Callable, Dict, Optional

from .config import MCP_SETTINGS

# Module logger; do not configure root logger here (entrypoint does that)
logger = logging.getLogger(__name__)

# Lazy Kroki client (avoids side-effects at import; testable via get_kroki_client)
_kroki_client = None


def get_kroki_client():
    """Return the Kroki client singleton. Lazy-initialized for testability."""
    global _kroki_client
    if _kroki_client is None:
        from kroki.kroki import Kroki

        _kroki_client = Kroki(base_url=MCP_SETTINGS.kroki_server)
    return _kroki_client


# Optional override for tests: if set, generate_diagram calls this instead of real I/O
_diagram_generator: Optional[
    Callable[[str, str, str, Optional[str]], Dict[str, Any]]
] = None


def set_diagram_generator(
    fn: Optional[Callable[[str, str, str, Optional[str]], Dict[str, Any]]],
) -> None:
    """Set an optional diagram generator (e.g. for tests). Pass None to use default."""
    global _diagram_generator
    _diagram_generator = fn


def generate_diagram(
    diagram_type: str,
    code: str,
    output_format: str = "png",
    output_dir: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a diagram using the appropriate service (Kroki, PlantUML, etc.)

    Args:
        diagram_type: Type of diagram (class, sequence, mermaid, d2, etc.)
        code: The diagram code/description
        output_format: Output format (png, svg, etc.)
        output_dir: Directory to save the generated image

    Returns:
        Dict containing code, URL, and local file path
    """
    if _diagram_generator is not None:
        return _diagram_generator(diagram_type, code, output_format, output_dir)

    logger.info(f"Generating {diagram_type} diagram")

    # Get the output directory (use default if not provided)
    if output_dir is None:
        output_dir = MCP_SETTINGS.output_dir

    # Ensure output directory exists
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"Using output directory: {output_dir}")

    # Get diagram configuration
    diagram_config = MCP_SETTINGS.diagram_types.get(diagram_type.lower())
    if not diagram_config:
        error_msg = f"Unsupported diagram type: {diagram_type}"
        logger.error(error_msg)
        return {"code": code, "error": error_msg}

    # Determine which backend service to use
    backend_type = diagram_config.backend

    # Handle different diagram types
    kroki_client = get_kroki_client()
    try:
        # Create filename prefix
        filename_prefix = (
            f"{diagram_type}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        )

        # Prepare code based on backend type
        if backend_type == "plantuml":
            # Ensure PlantUML markup is present
            if "@startuml" not in code:
                code = f"@startuml\n{code}"
            if "@enduml" not in code:
                code = f"{code}\n@enduml"

        # Generate diagram using Kroki service
        result = kroki_client.generate_diagram(backend_type, code, output_format)

        # If output directory is provided, save the image locally
        local_path = None
        if output_dir:
            local_path = os.path.join(output_dir, f"{filename_prefix}.{output_format}")
            with open(local_path, "wb") as f:
                f.write(result["content"])
            logger.info(f"Diagram saved to {local_path}")

        return {
            "code": code,
            "url": result["url"],
            "playground": result.get("playground"),
            "local_path": local_path,
        }

    except Exception as e:
        logger.error(f"Error generating diagram: {str(e)}")
        # Return partial result if possible
        return {
            "code": code,
            "url": None,
            "playground": None,
            "local_path": None,
            "error": str(e),
        }
