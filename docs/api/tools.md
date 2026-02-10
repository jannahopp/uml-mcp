# MCP Tools Reference

Two diagram tools are available. Both call [Kroki](https://kroki.io/) and support the diagram types listed under `uml://types`. Which output formats a type supports is in `uml://formats`.

## `generate_uml`

Generates a diagram and can save it to a directory if you pass one. If you omit `output_dir`, you still get `url`, `playground`, and `content_base64` (no file is written).

**Parameters:**

- `diagram_type` (string): Supported type (class, sequence, mermaid, d2, tikz, bpmn, graphviz, etc.). See `uml://types`.
- `code` (string): Diagram source in the syntax for that type.
- `output_dir` (string, optional): Directory to write the image. Omit for URL/base64 only.
- `output_format` (string, optional): svg, png, pdf, jpeg, txt, or base64 (default: svg). Allowed values depend on the diagram type; see `uml://formats`.
- `theme` (string, optional): PlantUML theme (e.g. cerulean) for PlantUML-based types.
- `scale` (number, optional): Scale factor for SVG only (default: 1.0, min: 0.1). Ignored for png, pdf, jpeg, etc.

**Returns:** JSON with `code`, `url`, `playground`; `local_path` when `output_dir` was set; `content_base64` when not saving; or `error` on failure.

**Example:**

```json
{
  "type": "tool",
  "name": "generate_uml",
  "args": {
    "diagram_type": "class",
    "code": "@startuml\nclass User\n@enduml",
    "output_dir": "./output"
  }
}
```

## `generate_diagram_url`

Returns the Kroki URL and optional base64 image. No file is written. Use it on read-only filesystems or when the client only needs a link or in-memory image.

**Parameters:**

- `diagram_type` (string): Same as for `generate_uml`; see `uml://types`.
- `code` (string): Diagram source in the syntax for that type.
- `output_format` (string, optional): svg, png, pdf, jpeg, etc. (default: svg). See `uml://formats` per type.
- `theme` (string, optional): PlantUML theme for PlantUML-based types.
- `scale` (number, optional): Scale factor for SVG only (default: 1.0, min: 0.1).

**Returns:** JSON with `code`, `url`, `playground`, and `content_base64` on success; or `error` on failure.

**Example:**

```json
{
  "type": "tool",
  "name": "generate_diagram_url",
  "args": {
    "diagram_type": "mermaid",
    "code": "graph TD; A-->B;"
  }
}
```

Use `generate_uml` when you might save to disk; use `generate_diagram_url` when you only need the URL or base64 and no file I/O.

## TikZ support

For `diagram_type: "tikz"`, `code` is TikZ/LaTeX source. You can pass a snippet (e.g. `\begin{tikzpicture}...\end{tikzpicture}`) or a full document; snippets are wrapped in a minimal standalone document. Supported output formats: **svg**, **pdf**, **png**, **jpeg**. Common TikZ libraries (e.g. shapes, arrows, positioning, pgfplots, automata) are inferred when possible. See [TikZ diagrams](../diagrams/tikz.md) for templates and examples.

**Example (TikZ):**

```json
{
  "type": "tool",
  "name": "generate_diagram_url",
  "args": {
    "diagram_type": "tikz",
    "code": "\\\\begin{tikzpicture}\\\\draw (0,0) circle (1cm);\\\\end{tikzpicture}",
    "output_format": "svg"
  }
}
```
