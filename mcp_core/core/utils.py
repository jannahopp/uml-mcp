"""
Utility functions for MCP server.

Logging is configured only by the CLI entrypoint (mcp_core.core.cli).
Kroki client is lazy-loaded for testability.
"""

import base64
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
        from tools.kroki.kroki import Kroki

        _kroki_client = Kroki(base_url=MCP_SETTINGS.kroki_server)
    return _kroki_client


# Optional override for tests: if set, generate_diagram calls this instead of real I/O
_diagram_generator: Optional[
    Callable[
        [str, str, str, Optional[str], Optional[str], float],
        Dict[str, Any],
    ]
] = None


def set_diagram_generator(
    fn: Optional[
        Callable[
            [str, str, str, Optional[str], Optional[str], float],
            Dict[str, Any],
        ]
    ],
) -> None:
    """Set an optional diagram generator (e.g. for tests). Pass None to use default."""
    global _diagram_generator
    _diagram_generator = fn


def _handle_diagram_error(e: Exception, code: str) -> str:
    """Return actionable error message for diagram generation failures."""
    try:
        from tools.kroki.kroki import KrokiConnectionError, KrokiHTTPError
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
    scale: float = 1.0,
) -> Dict[str, Any]:
    """
    Generate a diagram using Kroki first, with fallback to alternative services.

    Strategy: Always try Kroki first. If Kroki fails, fall back to:
    - PlantUML diagrams -> local PlantUML server
    - Mermaid diagrams -> mermaid.ink
    - Other diagrams -> return error (no fallback available)

    Args:
        diagram_type: Type of diagram (class, sequence, mermaid, d2, etc.)
        code: The diagram code/description
        output_format: Output format (png, svg, etc.)
        output_dir: Directory to save the generated image (optional). When None, no file is written (memory-only).
        theme: PlantUML theme (e.g. cerulean) - only for PlantUML backends
        scale: Scale factor for SVG (only when output_format is svg); default 1.0, min 0.1.

    Returns:
        Dict containing code, url, playground, local_path, and optional error; when not writing to file, content_base64 is included.
    """
    if _diagram_generator is not None:
        return _diagram_generator(
            diagram_type, code, output_format, output_dir, theme, scale
        )

    logger.info(f"Generating {diagram_type} diagram (Kroki first, fallback if needed)")

    # When output_dir is None, do not write to disk (memory-only); only explicit path triggers file I/O.
    # Ensure output directory exists when path was explicitly provided; on read-only FS skip write
    if output_dir:
        try:
            os.makedirs(output_dir, exist_ok=True)
            logger.debug(f"Using output directory: {output_dir}")
        except OSError as e:
            logger.warning(
                "Could not create output directory %s (%s); returning URL only.",
                output_dir,
                e,
            )
            output_dir = None

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

    backend_type = diagram_config.backend

    # Prepare code based on backend type. PlantUML gets @startuml/@enduml wrap; Mermaid/D2 sent as-is.
    prepared_code = code.strip()
    if backend_type == "plantuml":
        if "@startuml" not in prepared_code:
            prepared_code = f"@startuml\n{prepared_code}"
        if "@enduml" not in prepared_code:
            prepared_code = f"{prepared_code}\n@enduml"
        if theme and "!theme" not in prepared_code:
            prepared_code = prepared_code.replace(
                "@startuml", f"@startuml\n!theme {theme}"
            )

    # STEP 1: Try Kroki first (primary method)
    kroki_client = get_kroki_client()
    kroki_error = None
    try:
        filename_prefix = (
            f"{diagram_type}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        )

        logger.info(f"Attempting Kroki for {diagram_type} diagram")
        result = kroki_client.generate_diagram(
            backend_type, prepared_code, output_format
        )
        content = result["content"]
        if (
            output_format.lower() == "svg"
            and scale is not None
            and abs(scale - 1.0) >= 1e-9
            and scale >= 0.1
        ):
            from tools.kroki.kroki import scale_svg

            content = scale_svg(content, scale)

        local_path = None
        if output_dir:
            local_path = os.path.join(output_dir, f"{filename_prefix}.{output_format}")
            try:
                with open(local_path, "wb") as f:
                    f.write(content)
                logger.info(f"Diagram saved to {local_path}")
            except OSError as e:
                # Read-only filesystem (e.g. Vercel serverless): skip save, still return Kroki URL
                logger.warning(
                    "Could not save diagram to %s (%s); returning Kroki URL only.",
                    local_path,
                    e,
                )
                local_path = None

        out = {
            "code": prepared_code,
            "url": result["url"],
            "playground": result.get("playground"),
            "local_path": local_path,
        }
        # When not writing to file, include image in memory as base64 so clients can display without fetching URL.
        if local_path is None and content:
            out["content_base64"] = base64.b64encode(content).decode("ascii")
        
        logger.info(f"Successfully generated {diagram_type} diagram via Kroki")
        return out

    except Exception as e:
        kroki_error = e
        logger.warning(f"Kroki failed for {diagram_type}: {str(e)}. Attempting fallback...")

    # STEP 2: Kroki failed - try fallback methods based on backend type
    try:
        if backend_type == "plantuml":
            logger.info(f"Falling back to PlantUML server for {diagram_type}")
            return _generate_diagram_plantuml_fallback(
                diagram_type, prepared_code, output_format, output_dir, scale
            )
        elif backend_type == "mermaid":
            logger.info(f"Falling back to Mermaid.ink for {diagram_type}")
            return _generate_diagram_mermaid_fallback(
                diagram_type, prepared_code, output_format, output_dir
            )
        else:
            # No fallback available for this backend type
            logger.error(f"No fallback available for {backend_type} backend")
            raise kroki_error

    except Exception as fallback_error:
        logger.error(f"Fallback also failed for {diagram_type}: {str(fallback_error)}")
        error_msg = (
            f"Primary (Kroki) failed: {_handle_diagram_error(kroki_error, prepared_code)}. "
            f"Fallback also failed: {str(fallback_error)}"
        )
        return {
            "code": prepared_code,
            "url": None,
            "playground": None,
            "local_path": None,
            "error": error_msg,
        }
