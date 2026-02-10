# Examples

This folder is reserved for example configurations and alternative usage patterns.

**Per-type example files**

One example file per diagram type is generated from `DiagramExamples`. To regenerate them:

```bash
uv run python examples/generate_example_files.py
```

| File | diagram_type | How to render |
|------|--------------|---------------|
| example-class.puml | class | `generate_uml("class", code)` or Kroki `plantuml` |
| example-sequence.puml | sequence | `generate_uml("sequence", code)` or Kroki `plantuml` |
| example-activity.puml | activity | `generate_uml("activity", code)` or Kroki `plantuml` |
| example-usecase.puml | usecase | `generate_uml("usecase", code)` or Kroki `plantuml` |
| example-state.puml | state | `generate_uml("state", code)` or Kroki `plantuml` |
| example-component.puml | component | `generate_uml("component", code)` or Kroki `plantuml` |
| example-deployment.puml | deployment | `generate_uml("deployment", code)` or Kroki `plantuml` |
| example-object.puml | object | `generate_uml("object", code)` or Kroki `plantuml` |
| example-plantuml.puml | plantuml | `generate_uml("plantuml", code)` or Kroki `plantuml` |
| example-mermaid.mmd | mermaid | `generate_uml("mermaid", code)` or Kroki `mermaid` |
| example-d2.d2 | d2 | `generate_uml("d2", code)` or Kroki `d2` |
| example-graphviz.dot | graphviz | `generate_uml("graphviz", code)` or Kroki `graphviz` |
| example-erd.erd | erd | `generate_uml("erd", code)` or Kroki `erd` |
| example-blockdiag.txt | blockdiag | `generate_uml("blockdiag", code)` or Kroki `blockdiag` |
| example-seqdiag.txt | seqdiag | `generate_uml("seqdiag", code)` or Kroki `seqdiag` |
| example-actdiag.txt | actdiag | `generate_uml("actdiag", code)` or Kroki `actdiag` |
| example-nwdiag.txt | nwdiag | `generate_uml("nwdiag", code)` or Kroki `nwdiag` |
| example-packetdiag.txt | packetdiag | `generate_uml("packetdiag", code)` or Kroki `packetdiag` |
| example-rackdiag.txt | rackdiag | `generate_uml("rackdiag", code)` or Kroki `rackdiag` |
| example-bpmn.bpmn | bpmn | `generate_uml("bpmn", code)` or Kroki `bpmn` |
| example-c4plantuml.puml | c4plantuml | `generate_uml("c4plantuml", code)` or Kroki `c4plantuml` |
| example-bytefield.txt | bytefield | `generate_uml("bytefield", code)` or Kroki `bytefield` |
| example-dbml.dbml | dbml | `generate_uml("dbml", code)` or Kroki `dbml` |
| example-ditaa.txt | ditaa | `generate_uml("ditaa", code)` or Kroki `ditaa` |
| example-excalidraw.json | excalidraw | `generate_uml("excalidraw", code)` or Kroki `excalidraw` |
| example-nomnoml.txt | nomnoml | `generate_uml("nomnoml", code)` or Kroki `nomnoml` |
| example-pikchr.txt | pikchr | `generate_uml("pikchr", code)` or Kroki `pikchr` |
| example-structurizr.dsl | structurizr | `generate_uml("structurizr", code)` or Kroki `structurizr` |
| example-svgbob.txt | svgbob | `generate_uml("svgbob", code)` or Kroki `svgbob` |
| example-symbolator.txt | symbolator | `generate_uml("symbolator", code)` or Kroki `symbolator` |
| example-tikz.tex | tikz | `generate_uml("tikz", code)` or Kroki `tikz` |
| example-vega.json | vega | `generate_uml("vega", code)` or Kroki `vega` |
| example-vegalite.json | vegalite | `generate_uml("vegalite", code)` or Kroki `vegalite` |
| example-wavedrom.json | wavedrom | `generate_uml("wavedrom", code)` or Kroki `wavedrom` |
| example-wireviz.yaml | wireviz | `generate_uml("wireviz", code)` or Kroki `wireviz` |

Use resource `uml://types` for the full list of diagram types and `uml://templates` for starter code. See [Kroki](https://kroki.io/) for format details.

**Kroki URL generation:**

- `generate_kroki_url.py` (Option A, recommended): Uses the project's Kroki client to generate diagram URLs. Run: `uv run python examples/generate_kroki_url.py`
- `kroki_standalone_encoding.py` (Option B): Self-contained encoding utilities with no project dependencies. Copy this file if you need Kroki URL generation elsewhere.

**MCP server entrypoint:** The official way to run the UML-MCP server is:

- `python server.py` from the project root, or
- `uml-mcp` / `mcp-server` (Poetry/install console scripts that call `mcp_core.core.server:main`).

Legacy entrypoints (`mcp_server.py`, `mcp_serve2r.py`, `simplified_mcp_server.py`) were removed; all server logic lives in `mcp_core` and is started via `server.py`.

**REST API:** For the HTTP API (e.g. Vercel), run the FastAPI app: `uvicorn app:app`.
