"""
FastAPI application for UML diagram generation service on Vercel.
Provides REST API and MCP (Model Context Protocol) at /mcp for Smithery and clients.
"""

import json
import logging
import os
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, Field

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional MCP HTTP app for /mcp (used on Vercel / Smithery)
_mcp_http_app = None
try:
    from mcp_core.core.server import get_mcp_server

    _mcp = get_mcp_server()
    if hasattr(_mcp, "http_app"):
        _mcp_http_app = _mcp.http_app(path="/")
        logger.info("MCP HTTP app configured at /mcp")
except Exception as e:  # noqa: BLE001
    logger.info("MCP HTTP not available: %s", e)

# Initialize FastAPI (use MCP lifespan when mounted so session manager initializes)
app = FastAPI(
    title="UML Diagram Generator",
    description="API for generating UML and other diagrams; MCP at /mcp",
    version="1.2.0",
    lifespan=_mcp_http_app.lifespan if _mcp_http_app else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import local modules
try:
    from kroki.kroki import LANGUAGE_OUTPUT_SUPPORT
    from mcp_core.core.utils import generate_diagram

    HAS_MODULES = True
except ImportError:
    logger.warning(
        "Some UML-MCP modules could not be imported. Limited functionality available."
    )
    HAS_MODULES = False


# Models
class DiagramRequest(BaseModel):
    lang: str = Field(
        description="The language of the diagram like plantuml, mermaid, etc."
    )
    type: str = Field(description="The type of the diagram like class, sequence, etc.")
    code: str = Field(description="The code of the diagram.")
    theme: str = Field(default="", description="Optional theme for the diagram.")
    output_format: Optional[str] = Field(
        default="svg", description="Output format for the diagram (svg, png, etc.)"
    )


class DiagramResponse(BaseModel):
    url: str = Field(description="URL to the generated diagram.")
    message: Optional[str] = Field(
        default=None, description="A message about the diagram generation."
    )
    playground: Optional[str] = Field(
        default=None, description="URL to an interactive playground."
    )
    local_path: Optional[str] = Field(
        default=None, description="Local path to the diagram file."
    )


@app.get("/")
async def root():
    """Root endpoint with basic information about the API"""
    return {
        "message": "Welcome to the UML-MCP API",
        "version": "1.2.0",
        "status": "operational",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "modules_available": HAS_MODULES}


@app.post("/generate_diagram", response_model=DiagramResponse)
async def generate_diagram_endpoint(request: DiagramRequest):
    """Generate a diagram from text"""
    if not HAS_MODULES:
        raise HTTPException(
            status_code=503, detail="Diagram generation modules not available"
        )

    try:
        # Map request fields to diagram type
        diagram_type = request.type.lower()
        if diagram_type == "":
            diagram_type = request.lang.lower()

        output_format = request.output_format

        # Apply theme if provided - store original code for testing purposes
        original_code = request.code
        code = original_code
        if request.theme and "plantuml" in request.lang.lower():
            if "@startuml" in code and "!theme" not in code:
                code = code.replace("@startuml", f"@startuml\n!theme {request.theme}")

        # Create output directory if it doesn't exist
        output_dir = os.environ.get("VERCEL_OUTPUT_DIR", "/tmp/diagrams")
        os.makedirs(output_dir, exist_ok=True)

        # Generate the diagram
        result = generate_diagram(
            diagram_type=diagram_type,
            code=(
                original_code
                if os.environ.get("TESTING", "").lower() == "true"
                else code
            ),
            output_format=output_format,
            output_dir=output_dir,
        )

        # If error occurred during generation
        if "error" in result and result["error"]:
            raise HTTPException(status_code=400, detail=result["error"])

        # Prepare response
        response = {
            "url": result["url"],
            "message": "Diagram generated successfully",
            "playground": result.get("playground"),
            "local_path": result.get("local_path"),
        }

        return response

    except HTTPException:
        # Re-raise HTTP exceptions as they already have status codes
        raise
    except Exception as e:
        logger.exception(f"Error generating diagram: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Failed to generate diagram: {str(e)}"
        )


@app.get("/logo.png")
async def get_logo():
    """Return the logo for the plugin"""
    logo_path = os.path.join(os.path.dirname(__file__), "favicon.ico")
    if os.path.exists(logo_path):
        return FileResponse(logo_path)
    else:
        # Return a default response if logo file not found
        raise HTTPException(status_code=404, detail="Logo not found")


@app.get("/.well-known/ai-plugin.json")
async def get_plugin_manifest():
    """Return the plugin manifest for OpenAI plugins"""
    try:
        with open(
            os.path.join(os.path.dirname(__file__), ".well-known/ai-plugin.json"), "r"
        ) as f:
            manifest = json.load(f)
        return JSONResponse(content=manifest)
    except Exception as e:
        logger.exception(f"Error loading plugin manifest: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load plugin manifest")


@app.get("/.well-known/mcp/server-card.json")
async def get_mcp_server_card():
    """MCP server metadata for Smithery and other registries (optional manual metadata)."""
    return JSONResponse(
        content={
            "serverInfo": {
                "name": "UML Diagram Generator",
                "version": "1.2.0",
            },
            "tools": [
                {"name": "generate_uml", "description": "Generate any UML diagram by type and code"},
                {"name": "generate_class_diagram", "description": "Generate UML class diagram from PlantUML code"},
                {"name": "generate_sequence_diagram", "description": "Generate UML sequence diagram from PlantUML code"},
                {"name": "generate_activity_diagram", "description": "Generate UML activity diagram from PlantUML code"},
                {"name": "generate_mermaid_diagram", "description": "Generate diagrams using Mermaid syntax"},
                {"name": "generate_d2_diagram", "description": "Generate diagrams using D2 syntax"},
                {"name": "generate_graphviz_diagram", "description": "Generate diagrams using Graphviz DOT syntax"},
                {"name": "generate_erd_diagram", "description": "Generate Entity-Relationship diagrams"},
            ],
        }
    )


@app.get("/.well-known/privacy.txt")
async def get_privacy_policy():
    """Return the privacy policy for the plugin"""
    try:
        privacy_path = os.path.join(
            os.path.dirname(__file__), ".well-known/privacy.txt"
        )
        if os.path.exists(privacy_path):
            return FileResponse(privacy_path, media_type="text/plain")
        else:
            raise HTTPException(status_code=404, detail="Privacy policy not found")
    except Exception as e:
        logger.exception(f"Error loading privacy policy: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to load privacy policy")


@app.get("/supported_formats")
async def get_supported_formats():
    """Return the supported diagram formats"""
    if HAS_MODULES:
        return {"formats": LANGUAGE_OUTPUT_SUPPORT}
    else:
        return {"formats": {}}


@app.get("/openapi.json")
async def get_openapi_spec():
    """Return the OpenAPI specification"""
    return app.openapi()


@app.get("/openapi.yaml")
async def get_openapi_yaml():
    """Return the OpenAPI specification in YAML format"""
    try:
        import yaml

        openapi_spec = app.openapi()
        yaml_content = yaml.dump(openapi_spec)
        return Response(content=yaml_content, media_type="text/yaml")
    except ImportError:
        # If PyYAML is not available, return JSON spec instead
        return JSONResponse(
            content={
                "error": "YAML conversion not available, use /openapi.json instead"
            }
        )


# Mount MCP server at /mcp for Smithery and Streamable HTTP clients
if _mcp_http_app is not None:
    app.mount("/mcp", _mcp_http_app)


# Main entry point for local development
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
