# MCP Tools Reference

UML-MCP provides several MCP tools for diagram generation. These tools can be called by MCP clients like AI assistants.

## General Diagram Tool

### `generate_uml`

Generates a diagram of any supported type.

**Parameters:**
- `diagram_type` (string): Type of diagram (class, sequence, activity, etc.)
- `code` (string): The diagram code/description
- `output_dir` (string): Directory where to save the generated image

**Returns:**
JSON string containing:
- `code`: Original diagram code
- `url`: URL to the generated diagram
- `playground`: URL to an online playground (if available)
- `local_path`: Path to the saved image file

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

## UML Diagram Tools

### `generate_class_diagram`

Generates a class diagram.

**Parameters:**
- `code` (string): The PlantUML class diagram code
- `output_dir` (string): Directory where to save the generated image (optional)
- `output_format` (string): svg, png, or pdf (default: svg)
- `theme` (string): PlantUML theme (optional, e.g. cerulean)

**Returns:**
Same as `generate_uml`

### `generate_sequence_diagram`

Generates a sequence diagram.

**Parameters:**
- `code` (string): The PlantUML sequence diagram code
- `output_dir` (string): Directory where to save the generated image

**Returns:**
Same as `generate_uml`

### `generate_activity_diagram`

Generates an activity diagram.

**Parameters:**
- `code` (string): The PlantUML activity diagram code
- `output_dir` (string): Directory where to save the generated image

**Returns:**
Same as `generate_uml`

### `generate_usecase_diagram`

Generates a use case diagram.

**Parameters:**
- `code` (string): The PlantUML use case diagram code
- `output_dir` (string): Directory where to save the generated image

**Returns:**
Same as `generate_uml`

### Other UML Diagrams

Similar tools exist for other UML diagram types:
- `generate_state_diagram`
- `generate_component_diagram`
- `generate_deployment_diagram`
- `generate_object_diagram`

## Other Diagram Tools

### `generate_mermaid_diagram`

Generates a Mermaid diagram.

**Parameters:**
- `code` (string): The Mermaid diagram code
- `output_dir` (string): Directory where to save the generated image

**Returns:**
Same as `generate_uml`

### `generate_d2_diagram`

Generates a D2 diagram.

**Parameters:**
- `code` (string): The D2 diagram code
- `output_dir` (string): Directory where to save the generated image

**Returns:**
Same as `generate_uml`

### `generate_graphviz_diagram`

Generates a Graphviz diagram.

**Parameters:**
- `code` (string): The Graphviz (DOT) diagram code
- `output_dir` (string): Directory where to save the generated image

**Returns:**
Same as `generate_uml`

### `generate_erd_diagram`

Generates an Entity-Relationship diagram.

**Parameters:**
- `code` (string): The ERD diagram code
- `output_dir` (string): Directory where to save the generated image

**Returns:**
Same as `generate_uml`
