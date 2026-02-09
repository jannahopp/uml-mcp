# Configuration

UML-MCP can be configured using environment variables and MCP client config files.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_OUTPUT_DIR` / `UML_MCP_OUTPUT_DIR` | Directory to save generated diagrams | `./output` |
| `KROKI_SERVER` | URL of the Kroki server | `https://kroki.io` |
| `PLANTUML_SERVER` | URL of the PlantUML server | `http://plantuml-server:8080` |
| `USE_LOCAL_KROKI` | Use local Kroki server (true/false) | `false` |
| `USE_LOCAL_PLANTUML` | Use local PlantUML server (true/false) | `false` |

## MCP client configuration

Example MCP server config snippets for **Cursor** and **Claude Desktop** are in the **[`config/`](../config/)** folder in this repo:

- **`config/cursor_config.json`** — Cursor
- **`config/claude_desktop_config.json`** — Claude Desktop
- **`config/README.md`** — Where each app stores its config and how to copy the examples

Copy the relevant `mcpServers` block into your client’s config file and replace the placeholder path with your actual `uml-mcp` project path. The main server entry point is **`server.py`**.

## Advanced Configuration

### Custom Templates

You can customize diagram templates by modifying the templates in the `kroki/kroki_templates.py` file.

### Output Formats

Each diagram type supports specific output formats:

| Diagram Type | Supported Formats |
|--------------|-------------------|
| PlantUML     | png, svg, pdf, txt |
| Mermaid      | svg, png |
| D2           | svg, png |
| Graphviz     | png, svg, pdf, jpeg |

You can specify the output format when generating diagrams through the MCP tools.

## Server card and config schema (Smithery / quality score)

For better **Configuration UX** and MCP quality scores:

- The server card at `/.well-known/mcp/server-card.json` includes **tool annotations** (`readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint`) and a **config schema URL** (`configSchemaUrl`: `config-schema.json`).
- The session config schema is served at `/.well-known/mcp/config-schema.json` (same path as the card) so clients can resolve it when the card is loaded from that origin.
- When publishing via Smithery CLI, pass the config schema:  
  `npx @smithery/cli publish ... --config-schema smithery-config-schema.json`  
  See [Vercel/Smithery integration](integrations/vercel_smithery.md).
