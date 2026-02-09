# UML-MCP Documentation

Welcome to the documentation for UML-MCP, a diagram generation server with MCP interface.

## Overview

UML-MCP enables you to generate various types of diagrams through the Model Context Protocol (MCP), making it easy to integrate with AI assistants and other applications.

## User Manual (start here)

**[User Manual](user-manual.md)** — Install, configure, and use UML-MCP in one place: quick start (including Smithery), local installation, client setup (Cursor / Claude Desktop), environment variables, example prompts, tools overview, diagram types, troubleshooting, and links to deeper docs.

## Getting Started

- [Installation](installation.md)
- [Configuration](configuration.md)
- [Usage Examples](examples.md)
- [Diagram Assistant](diagram-assistant.md) — Example prompts (API sequence, Gantt, BPMN guide, convert class to Mermaid), tools, and resources.

## Diagram Types

- [UML Diagrams](diagrams/uml.md)
- [Mermaid Diagrams](diagrams/mermaid.md)
- [D2 Diagrams](diagrams/d2.md)
- [Other Diagram Types](diagrams/other.md)

## Integrations

- [Claude Desktop](integrations/claude_desktop.md)
- [Cursor](integrations/cursor.md)

## API Reference

- [MCP Tools](api/tools.md)
- [MCP Resources](api/resources.md)
- [MCP Prompts](api/prompts.md)

## Development

- [Contributing](development/contributing.md)
- [Architecture](development/architecture.md)
- [Local Setup](development/local-setup.md)

# Documentation

This project now uses MkDocs for documentation. To build the documentation, ensure you have MkDocs installed and run:

```bash
mkdocs serve
```

## Features Added

- Added `rich` for better terminal output.
- Added `typer` for CLI building.
- Added `uvloop` for improved event loop performance.
- Added `poetry` for dependency management.

Refer to the `mkdocs.yml` file for configuration details.
