# Cursor Integration

This guide explains how to integrate UML-MCP with Cursor for generating diagrams directly in your editor.

## Overview

Cursor can connect to the UML-MCP server through the Model Context Protocol (MCP), allowing you to generate and visualize UML diagrams and other supported diagram types while you code.

## Setup Instructions

### 1. Install and Configure UML-MCP

Make sure you have the UML-MCP server properly installed and configured on your system. See the [Installation](../installation.md) guide for details.

### 2. Cursor Configuration

Cursor requires specific configuration to connect to the UML-MCP server:

1. Locate your Cursor configuration file:
   - Windows: `%APPDATA%\Cursor\config.json`
   - macOS: `~/Library/Application Support/Cursor/config.json`
   - Linux: `~/.config/Cursor/config.json`

2. Add the UML-MCP server configuration to the `mcpServers` section:

Example configuration (see also the **`config/cursor_config.json`** and **`config/README.md`** in the repo):

```json
{
  "mcpServers": {
    "UML-MCP-Server": {
      "command": "python",
      "args": ["/path/to/uml-mcp/server.py"],
      "cwd": "/path/to/uml-mcp"
    }
  }
}
```

### 3. Test the Integration

1. Restart Cursor after saving the configuration
2. In a conversation with Cursor, ask it to create a UML diagram
3. Cursor should be able to generate the diagram using the UML-MCP server

Example prompt:
```
Create a UML class diagram for the current project structure.
```

## Troubleshooting

### Server Connection Issues

If Cursor cannot connect to the UML-MCP server:

1. Verify the server is running by launching it manually first
2. Check paths in your configuration are correct and absolute
3. Ensure you have the required permissions for the directories
4. Check Cursor logs for connection errors

### Diagram Generation Problems

If diagrams aren't being generated correctly:

1. Verify the UML-MCP server is running without errors
2. Check the output directory permissions
3. Try generating different diagram types to isolate the issue
4. Verify that all required dependencies are installed

## Advanced Configuration

### Custom Templates

You can customize how diagrams appear in Cursor by modifying the templates in the UML-MCP server. See [Advanced Configuration](../configuration.md#custom-templates) for details.

### Output Formats

Cursor works well with SVG and PNG formats. You can specify the preferred format in your prompts or configure defaults in the UML-MCP server.

## Related Resources

- [Configuration Options](../configuration.md)
- [UML Diagram Examples](../examples.md)
- [Supported Diagram Types](../diagrams/uml.md)
