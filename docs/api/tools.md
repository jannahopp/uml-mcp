# MCP Tools Reference

UML-MCP exposes a single MCP tool for diagram generation. Use the `uml://types` resource to see valid diagram types.

## `generate_uml`

Generates a diagram of any supported type. Pass `diagram_type` (e.g. class, sequence, activity, mermaid, d2, bpmn) and the corresponding `code` in that syntax.

**Parameters:**
- `diagram_type` (string): Type of diagram (class, sequence, activity, use case, state, component, deployment, object, mermaid, d2, graphviz, erd, blockdiag, bpmn, c4plantuml). Use `uml://types` for the full list.
- `code` (string): The diagram code in the syntax for the chosen type (e.g. PlantUML, Mermaid, D2).
- `output_dir` (string, optional): Directory where to save the generated image.
- `output_format` (string, optional): svg, png, or pdf (default: svg). See `uml://formats` for supported formats per type.
- `theme` (string, optional): PlantUML theme for UML diagram types (e.g. cerulean).

**Returns:**
JSON containing:
- `code`: Original diagram code
- `url`: URL to the generated diagram
- `playground`: URL to an online playground (if available)
- `local_path`: Path to the saved image file (if `output_dir` was provided)
- `error`: Present only if validation or generation failed

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

For class diagrams use `diagram_type`: `"class"`; for sequence use `"sequence"`; for Mermaid use `"mermaid"`; for D2 use `"d2"`; and so on.
