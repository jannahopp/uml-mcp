# Examples

This folder is reserved for example configurations and alternative usage patterns.

**Kroki URL generation:**

- `generate_kroki_url.py` (Option A, recommended): Uses the project's Kroki client to generate diagram URLs. Run: `python examples/generate_kroki_url.py`
- `kroki_standalone_encoding.py` (Option B): Self-contained encoding utilities with no project dependencies. Copy this file if you need Kroki URL generation elsewhere.

**MCP server entrypoint:** The official way to run the UML-MCP server is:

- `python server.py` from the project root, or
- `uml-mcp` / `mcp-server` (Poetry/install console scripts that call `mcp_core.core.server:main`).

Legacy entrypoints (`mcp_server.py`, `mcp_serve2r.py`, `simplified_mcp_server.py`) were removed; all server logic lives in `mcp_core` and is started via `server.py`.

**REST API:** For the HTTP API (e.g. Vercel), run the FastAPI app: `uvicorn app:app`.
