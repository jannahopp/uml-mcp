"""
Generate static MCP server-card.json for Vercel.
Vercel reserves /.well-known for SSL and does not allow rewrites to serverless
functions, so we serve the server card as a static file at .well-known/mcp/server-card.json.
Run from repo root: python scripts/generate_server_card.py
"""

import json
import os
import sys

# Ensure project root is on path
repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)


def build_server_card():
    """Build server card dict from tool and resource registries (mirrors app._build_server_card)."""
    try:
        from mcp_core.core.config import MCP_SETTINGS
        from mcp_core.resources.diagram_resources import get_resource_registry
        from mcp_core.tools.tool_decorator import get_tool_registry

        tool_registry = get_tool_registry()
        resource_registry = get_resource_registry()

        tools = []
        for name, info in tool_registry.items():
            params = info.get("parameters", {})
            properties = {}
            required = []
            for pname, pinfo in params.items():
                py_type = pinfo.get("type", "str")
                js_type = (
                    "string"
                    if py_type in ("str", "Optional[str]")
                    else "boolean"
                    if py_type == "bool"
                    else "integer"
                    if py_type == "int"
                    else "string"
                )
                properties[pname] = {
                    "type": js_type,
                    "description": pname.replace("_", " ").title(),
                }
                if pinfo.get("required", True):
                    required.append(pname)
            tools.append(
                {
                    "name": name,
                    "description": info.get("description", ""),
                    "inputSchema": {
                        "type": "object",
                        "properties": properties,
                        "required": required,
                    },
                }
            )

        resources = []
        for uri, info in resource_registry.items():
            resources.append(
                {
                    "uri": uri,
                    "name": uri,
                    "description": info.get("description", ""),
                }
            )

        return {
            "serverInfo": {
                "name": MCP_SETTINGS.display_name,
                "version": MCP_SETTINGS.version,
            },
            "tools": tools,
            "resources": resources,
            "prompts": [],
        }
    except Exception as e:
        print(f"Warning: {e}", file=sys.stderr)
        return {
            "serverInfo": {"name": "UML Diagram Generator", "version": "1.2.0"},
            "tools": [],
            "resources": [],
            "prompts": [],
        }


def main():
    card = build_server_card()
    # Write to .well-known/ (for local/dev)
    out_dir = os.path.join(repo_root, ".well-known", "mcp")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "server-card.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(card, f, indent=2)
    print(f"Wrote {out_path}")
    # Write to public/ (Vercel serves this at root - required for Smithery)
    public_dir = os.path.join(repo_root, "public", ".well-known", "mcp")
    os.makedirs(public_dir, exist_ok=True)
    public_path = os.path.join(public_dir, "server-card.json")
    with open(public_path, "w", encoding="utf-8") as f:
        json.dump(card, f, indent=2)
    print(f"Wrote {public_path}")


if __name__ == "__main__":
    main()
