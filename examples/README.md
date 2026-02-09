# Examples

This folder is reserved for example configurations and alternative usage patterns.

**MCP server entrypoint:** The official way to run the UML-MCP server is:

- `python server.py` from the project root, or
- `uml-mcp` / `mcp-server` (Poetry/install console scripts that call `mcp_core.core.server:main`).

Legacy entrypoints (`mcp_server.py`, `mcp_serve2r.py`, `simplified_mcp_server.py`) were removed; all server logic lives in `mcp_core` and is started via `server.py`.

**REST API:** For the HTTP API (e.g. Vercel), run the FastAPI app: `uvicorn app:app`.
