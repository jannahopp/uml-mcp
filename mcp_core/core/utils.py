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
    Callable[[str, str, str, Optional[str], Optional[str]], Dict[str, Any]]
] = None


def set_diagram_generator(
    fn: Optional[
        Callable[[str, str, str, Optional[str], Optional[str]], Dict[str, Any]]
    ],
) -> None:
    """Set an optional diagram generator (e.g. for tests). Pass None to use default."""
    global _diagram_generator
    _diagram_generator = fn


def _handle_diagram_error(e: Exception, code: str) -> str:
    """Return actionable error message for diagram generation failures."""
    try:
        from kroki.kroki import KrokiConnectionError, KrokiHTTPError
    except ImportError:
        return f"Unexpected error generating diagram: {type(e).__name__}: {str(e)}"

    if isinstance(e, KrokiHTTPError):
        status = getattr(e.response, "status_code", None)
        if status == 404:
            return (
                "Diagram service endpoint not found. Check KROKI_SERVER and that "
                "the service is running."
            )
        if status == 503:
            return (
                "Diagram service temporarily unavailable. Check KROKI_SERVER and "
                "network connectivity."
            )
        if status == 400:
            return (
                "Diagram code syntax error. Check examples at uml://examples resource "
                "for valid syntax."
            )
        return (
            f"Diagram service returned HTTP {status}. Check KROKI_SERVER and network."
        )
    if isinstance(e, KrokiConnectionError):
        return (
            "Cannot connect to diagram service. Check KROKI_SERVER and network "
            "connectivity."
        )
    return f"Unexpected error generating diagram: {type(e).__name__}: {str(e)}"


def generate_diagram(
    diagram_type: str,
    code: str,
    output_format: str = "png",
    output_dir: Optional[str] = None,
    theme: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Generate a diagram using the appropriate service (Kroki, PlantUML, etc.)

    Args:
        diagram_type: Type of diagram (class, sequence, mermaid, d2, etc.)
        code: The diagram code/description
        output_format: Output format (png, svg, etc.)
        output_dir: Directory to save the generated image
        theme: PlantUML theme (e.g. cerulean) - only for PlantUML backends

    Returns:
        Dict containing code, url, playground, local_path, and optional error
    """
    if _diagram_generator is not None:
        return _diagram_generator(diagram_type, code, output_format, output_dir, theme)

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

    # Determine which backend service to use
    backend_type = diagram_config.backend

    # Prepare code based on backend type
    prepared_code = code
    if backend_type == "plantuml":
        if "@startuml" not in prepared_code:
            prepared_code = f"@startuml\n{prepared_code}"
        if "@enduml" not in prepared_code:
            prepared_code = f"{prepared_code}\n@enduml"
        if theme and "!theme" not in prepared_code:
            prepared_code = prepared_code.replace(
                "@startuml", f"@startuml\n!theme {theme}"
            )

    kroki_client = get_kroki_client()
    try:
        filename_prefix = (
            f"{diagram_type}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        )

        result = kroki_client.generate_diagram(
            backend_type, prepared_code, output_format
        )

        local_path = None
        if output_dir:
            local_path = os.path.join(output_dir, f"{filename_prefix}.{output_format}")
            with open(local_path, "wb") as f:
                f.write(result["content"])
            logger.info(f"Diagram saved to {local_path}")

        return {
            "code": prepared_code,
            "url": result["url"],
            "playground": result.get("playground"),
            "local_path": local_path,
        }

    except Exception as e:
        logger.error(f"Error generating diagram: {str(e)}")
        error_msg = _handle_diagram_error(e, prepared_code)
        return {
            "code": prepared_code,
            "url": None,
            "playground": None,
            "local_path": None,
            "error": error_msg,
        }
