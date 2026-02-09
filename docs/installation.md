# Installation

This guide explains how to install and set up the UML-MCP server.

## System Requirements

- Python 3.10 or higher
- [uv](https://docs.astral.sh/uv/), [Poetry](https://python-poetry.org/), or pip
- Optional: Docker for running local PlantUML or Kroki servers

## Installation Steps

1. Clone the repository:

```bash
git clone https://github.com/yourusername/uml-mcp.git
cd uml-mcp
```

2. Install the dependencies:

**With uv (recommended):**

```bash
uv sync
```

**With Poetry:**

```bash
poetry install
```

**With pip:**

```bash
pip install -r requirements.txt
```

3. For development (tests, linting):

```bash
uv sync --all-groups
# or: poetry install --with dev
# or: pip install -r requirements-dev.txt
```

## Verifying Installation

To verify your installation:

```bash
python server.py --list-tools
```

You should see output similar to:

```
Starting UML-MCP Server v1.2.0
Server Name: UML Diagram Generator
Available Tools: 12
Available Prompts: 3
```

## IDE Integration

### Cursor and other MCP clients

Configure your IDE to run the UML-MCP server. Use **manual configuration**:

- **Command**: `python` (or full path to your venv Python if using uv/Poetry)
- **Arguments**: `["/path/to/uml-mcp/server.py"]` — use the **full path** to `server.py`
- **Working directory**: `/path/to/uml-mcp` (project root)
- **Output directory**: Optional; set `MCP_OUTPUT_DIR` in env or use default `./output`

See [config/README.md](../config/README.md) for where each app stores its config, and [Cursor integration](integrations/cursor.md) or [Claude Desktop integration](integrations/claude_desktop.md) for step-by-step setup.

## Optional Components

### Local Diagram Servers

For better performance or offline use, you can set up local servers:

#### PlantUML Server

```bash
docker run -d -p 8080:8080 plantuml/plantuml-server
```

#### Kroki Server

```bash
docker run -d -p 8000:8000 yuzutech/kroki
```

## Troubleshooting

If you encounter issues during installation:

1. Ensure Python 3.10+ is installed and in your PATH
2. Check that all required dependencies are installed
3. Verify any local servers are running correctly
4. Ensure proper permissions for the output directory
