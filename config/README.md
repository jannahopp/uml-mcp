# MCP client configuration examples

This folder holds **example** MCP server config snippets for UML-MCP. Copy the relevant block into your client’s config file and replace the paths with your actual `uml-mcp` install path.

## Cursor

- **File**:  
  - Windows: `%APPDATA%\Cursor\User\globalStorage\cursor.mcp\mcp.json` or Cursor Settings → MCP  
  - macOS: `~/Library/Application Support/Cursor/User/globalStorage/cursor.mcp/mcp.json`  
  - Linux: `~/.config/Cursor/User/globalStorage/cursor.mcp/mcp.json`  

- **Example**: `cursor_config.json`  
  - Replace `C:\path\to\uml-mcp` (Windows) or `/path/to/uml-mcp` (macOS/Linux) with your repo path.  
  - Optional: add `"env": { "MCP_OUTPUT_DIR": "C:\\path\\to\\output" }` to set the diagram output directory.

## Claude Desktop

- **File**:  
  - Windows: `%APPDATA%\Claude\claude_desktop_config.json`  
  - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`  

- **Example**: `claude_desktop_config.json`  
  - Replace `C:\path\to\uml-mcp` (or `/path/to/uml-mcp` on macOS) with your repo path.  
  - Optional: add `"env": { "MCP_OUTPUT_DIR": "C:\\path\\to\\output" }` for diagram output.

## Notes

- Use the **full path** to `server.py` in `args`.
- `cwd` should be the project root (the folder that contains `server.py`).
- If you use a virtualenv or Poetry, you can set `"command"` to the full path to that Python, e.g. `"C:\\path\\to\\uml-mcp\\.venv\\Scripts\\python.exe"` (Windows) or `"/path/to/uml-mcp/.venv/bin/python"` (macOS/Linux).
