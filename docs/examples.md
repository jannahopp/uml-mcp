# Usage Examples

This page provides examples of using UML-MCP with different environments and diagram types.

## Basic Usage with Cursor

When using Cursor with UML-MCP configured, you can generate diagrams by asking the AI assistant:

```
Generate a class diagram for a banking system with Account, Customer, and Transaction classes.
```

The AI will use UML-MCP's tools to generate and display the diagram directly in your conversation.

## AI Assistant Prompts

Here are some example prompts for generating diagrams:

### Class Diagram

```
Create a class diagram showing the relationships between the following classes:
- Person (name, age, email)
- Student (studentId, enrollCourse())
- Teacher (employeeId, teachCourse())
- Course (courseId, title, description)

Students can enroll in multiple courses, and each course can have one teacher.
```

### Sequence Diagram

```
Generate a sequence diagram for an e-commerce checkout process involving:
- Customer
- ShoppingCart
- OrderSystem
- PaymentProcessor
- InventorySystem
```

### Component Diagram

```
Create a component diagram for a microservices architecture with:
- API Gateway
- User Service
- Product Service
- Order Service
- Payment Service
- Notification Service
```

## Diagram assistant (example prompts)

The server supports a diagram-assistant workflow for common requests. Use these example prompts with your MCP client (e.g. Cursor, Claude Desktop); the assistant will use the right tools, resources, and prompts.

| User prompt | What happens | Tools / resources |
|-------------|--------------|-------------------|
| **Show me a Mermaid sequence diagram for an API call** | Returns a Mermaid `sequenceDiagram` (client → API → backend) and can render it. | Prompt: `mermaid_sequence_api`. Resource: `uml://mermaid-examples` (key `sequence_api`). Tool: `generate_uml("mermaid", code)`. |
| **Generate a Gantt chart using Mermaid syntax** | Returns a Mermaid `gantt` block and can render it. | Prompt: `mermaid_gantt`. Resource: `uml://mermaid-examples` (key `gantt`). Tool: `generate_uml("mermaid", code)`. |
| **Explain how to draw a BPMN process model** | Explains BPMN 2.0.2 elements (events, tasks, gateways, flow, lanes) and how to generate BPMN. | Prompt: `bpmn_process_guide`. Resource: `uml://bpmn-guide`. Tool: `generate_bpmn_diagram` or `generate_uml("bpmn", code)`. |
| **Convert this class diagram into Mermaid code** | Converts PlantUML or prose class diagram to Mermaid `classDiagram` and can render it. | Prompt: `convert_class_to_mermaid`. Tool: `generate_uml("mermaid", code)`. |

**Resources**

- `uml://types` — Supported diagram types (including `mermaid`, `bpmn`, `packetdiag`).
- `uml://templates` — Starter templates per diagram type.
- `uml://examples` — Full examples per diagram type.
- `uml://mermaid-examples` — Mermaid API sequence and Gantt examples.
- `uml://bpmn-guide` — BPMN 2.0.2 process modeling guide.

**Public references (syntax and specs)**

- [Kroki](https://kroki.io) — Supported diagram types and rendering.
- [Mermaid](https://mermaid.js.org) — Mermaid syntax (sequence, gantt, classDiagram, etc.).
- [OMG BPMN 2.0.2](https://www.omg.org/spec/BPMN/2.0.2) — BPMN specification.

## Using MCP Tools Directly

If you're building an application that uses UML-MCP, you can call the tools directly:

### Python Example

```python
import json
import subprocess

def generate_class_diagram(code):
    # Start the MCP server process
    process = subprocess.Popen(
        ["python", "server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Prepare MCP request (use generate_uml with diagram_type for any diagram)
    request = {
        "type": "tool",
        "name": "generate_uml",
        "args": {
            "diagram_type": "class",
            "code": code,
            "output_dir": "./output"
        }
    }

    # Send request to MCP server
    process.stdin.write(json.dumps(request) + "\n")
    process.stdin.flush()

    # Read response
    response = json.loads(process.stdout.readline())

    # Close process
    process.terminate()

    return json.loads(response["result"])

# Example usage (PlantUML class diagram)
diagram = generate_class_diagram("""
@startuml
class User {
  -name: String
  -email: String
  +register(): void
  +login(): boolean
}
@enduml
""")

print(f"Diagram URL: {diagram['url']}")
print(f"Local file: {diagram['local_path']}")
```

## Integration Examples

### Web Application

```javascript
async function generateDiagram(diagramType, code) {
  const response = await fetch('/api/diagram', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      type: diagramType,
      code: code
    }),
  });

  const result = await response.json();
  document.getElementById('diagram').src = result.url;
  document.getElementById('playground-link').href = result.playground;
}
```

### Command Line

```bash
echo '{
  "type": "tool",
  "name": "generate_uml",
  "args": {
    "diagram_type": "sequence",
    "code": "@startuml\nAlice -> Bob: Hello\nBob --> Alice: Hi\n@enduml",
    "output_dir": "./diagrams"
  }
}' | python server.py
```
