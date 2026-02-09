# UML-MCP: Diagram Generation Server with MCP Interface

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![smithery badge](https://smithery.ai/badge/@antoinebou12/uml)](https://smithery.ai/server/@antoinebou12/uml)
[![MseeP.ai Security Assessment](https://img.shields.io/badge/MseeP.ai-Security%20Assessment-green)](https://mseep.ai/app/antoinebou12-uml-mcp)

UML-MCP is a diagram generation server that implements the Model Context Protocol (MCP), so you can create diagrams from AI assistants and other MCP clients.

## Features

- **Multiple diagram types**: UML (Class, Sequence, Activity, Use Case, State, Component, Deployment, Object), Mermaid, D2, Graphviz, ERD, BlockDiag, BPMN, C4 with PlantUML
- **MCP integration**: Works with any client that supports MCP (Cursor, Claude Desktop, etc.)
- **Output formats**: SVG, PNG, PDF, and others depending on diagram type
- **Configurable backends**: Local or remote PlantUML and Kroki

## Supported diagram types

| Category | Diagram types |
|----------|----------------|
| UML      | Class, Sequence, Activity, Use Case, State, Component, Deployment, Object |
| Other    | Mermaid, D2, Graphviz, ERD, BlockDiag, BPMN, C4 (PlantUML) |

## Getting started

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/), [Poetry](https://python-poetry.org/), or pip

### Installation

**With uv (recommended, modern Python):**

```bash
git clone https://github.com/yourusername/uml-mcp.git
cd uml-mcp
uv sync
```

**With Poetry:**

```bash
git clone https://github.com/yourusername/uml-mcp.git
cd uml-mcp
poetry install
```

**With pip:**

```bash
git clone https://github.com/yourusername/uml-mcp.git
cd uml-mcp
pip install -e .
```

For development (tests, linting, type checking) you must install dev dependencies:

```bash
uv sync --all-groups
# or: poetry install --with dev
# or: pip install -e ".[dev]"
```

Without `--all-groups`, tools like black, flake8, isort are not installed and `uv run python -m black` will fail with "No module named black". Dev tools: ruff (lint + format), ty (type check), pytest, pytest-cov, black, flake8, isort, pre-commit.

### Running the server

**MCP server (single CLI entrypoint):** `server.py` is the official MCP server; the FastAPI app in `app.py` is the separate REST API (e.g. for Vercel).

**Canonical entry point** (MCP server using mcp_core and Kroki):

From the project root:

```bash
python server.py
```

Or with uv / Poetry:

```bash
uv run python server.py
# or: poetry run python server.py
# or: poetry run uml-mcp
```

The server uses stdio by default. For HTTP:

```bash
python server.py --transport http --host 127.0.0.1 --port 8000
```

List available tools and exit:

```bash
python server.py --list-tools
```

## Configuration

### MCP client setup

Example MCP server configs are in the **`config/`** folder:

- **`config/cursor_config.json`** — snippet for Cursor
- **`config/claude_desktop_config.json`** — snippet for Claude Desktop

Copy the relevant block into your client’s config and replace `/path/to/uml-mcp` with the real path to this repo. See **`config/README.md`** for where each app stores its config.

### Environment variables

| Variable            | Description                          | Default                    |
|---------------------|--------------------------------------|----------------------------|
| `MCP_OUTPUT_DIR`    | Directory for generated diagrams     | `./output`                 |
| `UML_MCP_OUTPUT_DIR`| Same as above (alternative name)     | —                          |
| `KROKI_SERVER`      | Kroki server URL                      | `https://kroki.io`         |
| `PLANTUML_SERVER`   | PlantUML server URL                  | `http://plantuml-server:8080` |
| `USE_LOCAL_KROKI`   | Use local Kroki (`true`/`false`)      | `false`                    |
| `USE_LOCAL_PLANTUML`| Use local PlantUML (`true`/`false`)   | `false`                    |
| `LOG_LEVEL`         | Logging level                         | —                          |
| `LIST_TOOLS`        | Set to `true` to list tools and exit | —                          |

Full options are documented in [docs/configuration.md](docs/configuration.md) and [docs/installation.md](docs/installation.md).

## Local development

Run PlantUML and/or Kroki locally (e.g. with Docker):

```bash
# PlantUML
docker run -d -p 8080:8080 plantuml/plantuml-server

# Kroki
docker run -d -p 8000:8000 yuzutech/kroki
```

Then:

```bash
export USE_LOCAL_PLANTUML=true
export PLANTUML_SERVER=http://localhost:8080
export USE_LOCAL_KROKI=true
export KROKI_SERVER=http://localhost:8000
python server.py
```

## Architecture

- **MCP server**: `server.py` (entry point), `mcp_core/` (server, config, tools, resources, prompts)
- **Diagram backends**: `plantuml/`, `kroki/`, `mermaid/`, `D2/`
- **Tools**: Diagram generation tools are registered in `mcp_core/tools/` and exposed via MCP
- **Resources**: Templates and examples under the `uml://` URI scheme

## MCP resources and tools

**Resources (e.g. `uml://types`, `uml://templates`, `uml://examples`, `uml://formats`, `uml://server-info`, `uml://workflow`)**
Provide diagram types, templates, examples, formats, server info, and the recommended workflow for complex diagrams.

**Tools** include:

- `generate_uml` — any UML diagram (params: `diagram_type`, `code`, `output_dir`)
- `generate_class_diagram`, `generate_sequence_diagram`, `generate_activity_diagram`, etc.
- `generate_mermaid_diagram`, `generate_d2_diagram`, `generate_graphviz_diagram`, `generate_erd_diagram`
- `sequentialthinking` — plan and verify diagram design step-by-step before generating (see below)

See [docs/api/tools.md](docs/api/tools.md) for full tool list and parameters.

### Better results for complex diagrams

For complex or ambiguous diagram requests, use the **uml_diagram_with_thinking** prompt or the **sequentialthinking** tool to plan and verify the design (diagram type, elements, relationships) before calling `generate_uml` with the final code. The resource `uml://workflow` describes this recommended flow. To reduce log noise from thought steps, set `DISABLE_THOUGHT_LOGGING=true` (see [docs/configuration.md](docs/configuration.md)). The `sequentialthinking` tool mirrors the Node sequential-thinking server API for compatibility with clients that expect that workflow.

## Tests

See [Testing](docs/testing.md) for why integration tests are skipped by default and how to run them. Use the project’s venv so pytest-cov and options from `pyproject.toml` apply:

```bash
uv run pytest tests/ -v
# or: poetry run pytest tests/ -v
```

Do not run bare `pytest` (system Python); it may not have pytest-cov and will not see the project’s addopts.

**Integration tests (MCP Client)** use the real FastMCP package and an in-process client to test discovery and tools. They are skipped unless `USE_REAL_FASTMCP=1` is set. Run them with:

```bash
USE_REAL_FASTMCP=1 uv run pytest tests/integration -v
```

These tests require a fastmcp version that provides `fastmcp.client.Client` (e.g. FastMCP 2.x / 3.x). Diagram generation is mocked so no network call to Kroki is made.

### Lint and type check

```bash
uv run ruff check .
uv run ruff format --check .
# or: make lint

# Optional type checking (gradual adoption):
uv run ty check
# or: make typecheck
```

- If you see **No module named black** (or flake8/isort), run `uv sync --all-groups` so dev tools are installed.
- If you get **Permission denied** when running `uv run black` / `flake8` / `isort` (e.g. on WSL with project on `/mnt/c/`), use the module form: `uv run python -m black ...`, `uv run python -m flake8 ...`, `uv run python -m isort ...`, or fix execute bits: `chmod +x .venv/bin/black .venv/bin/flake8 .venv/bin/isort`.

### Testing the CI pipeline locally

**Option 1: Same steps as CI, no Docker**

```bash
make ci
```

Runs lint (ruff) and tests with coverage, matching the test job in `.github/workflows/ci.yml`.

**Option 2: act (GitHub Actions in Docker)**

You can run the full workflow locally with [act](https://github.com/nektos/act). Requires Docker. The main pipeline is in a single file (`.github/workflows/ci.yml`) so `act push` runs test and build jobs without reusable-workflow issues.

**Install act (Windows):** Chocolatey `choco install act-cli -y`, Scoop `scoop install act`, or download from [act releases](https://github.com/nektos/act/releases).

```bash
act -l
act push
```

## Documentation

- [Installation](docs/installation.md)
- [Configuration](docs/configuration.md)
- [API / tools](docs/api/tools.md)
- [Cursor integration](docs/integrations/cursor.md)
- [Claude Desktop integration](docs/integrations/claude_desktop.md)

## Contributing and community

- [Contributing guide](CONTRIBUTING.md) — setup, tests, and how to send pull requests
- [Code of conduct](CODE_OF_CONDUCT.md)
- [Security policy](SECURITY.md) — how to report vulnerabilities

## License

MIT — see [LICENSE](LICENSE).

## Acknowledgements

- [PlantUML](https://plantuml.com/)
- [Kroki](https://kroki.io/)
- [Mermaid](https://mermaid.js.org/)
- [D2](https://d2lang.com/)
