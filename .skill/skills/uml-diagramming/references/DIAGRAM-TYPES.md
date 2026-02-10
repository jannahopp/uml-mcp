# Diagram Type Mappings and Constraints

Full reference for mapping user-requested diagram types to Mermaid and PlantUML syntax, and optional constraints.

## Mermaid: Diagram Type → Syntax

| Diagram Type | Mermaid Form | Notes |
|--------------|--------------|--------|
| Sequence | `sequenceDiagram` | Use `participant`, `actor`, `alt`/`opt`/`loop`. |
| Class | `classDiagram` | Visibility: `+` `-` `#`; relationships with multiplicities. |
| State | `stateDiagram-v2` | `[*]` start/end; `-->` with labels. |
| Activity | `flowchart` | Use `flowchart TB`; start/end nodes; diamonds for decisions. |
| Component | `flowchart` + subgraphs | Group components in `subgraph name [Label]`. |
| Deployment | `flowchart` + subgraphs | Nodes and edges; subgraphs for tiers. |
| Network | `flowchart` + subgraphs | Same as deployment; label protocols on edges. |
| Gantt | `gantt` | `title`, `dateFormat`, sections, tasks. |
| MindMap | `mindmap` | Root and children. |
| WBS | `mindmap` or `flowchart` | Tree structure. |
| Use Case | `flowchart` | Actors as nodes; use cases as nodes; group in subgraph. |
| Object | `classDiagram` with notes, or `flowchart` | Instances and links. |
| Timing | `sequenceDiagram` | Add timing/ordering notes. |
| Wireframe / Archimate | `flowchart` | Boxes and groupings. |
| JSON / YAML | `flowchart` | Represent structure as nodes/edges; do not embed raw JSON/YAML in a mermaid block. |

## PlantUML: Diagram Type → Syntax

| Diagram Type | PlantUML Form | Notes |
|--------------|---------------|--------|
| Sequence | `@startuml` … sequence … `@enduml` | `participant`, `actor`, `database`, `alt`/`opt`/`loop`. |
| Use Case | usecase diagram | `actor`, `usecase`, `rectangle` for system boundary. |
| Class | class diagram | `class`, `interface`; relationships with multiplicities. |
| Activity | activity diagram | `start`, `stop`, `if`/`else`/`endif`, `fork`/`end fork`. |
| Component | component diagram | `component`, `interface`, dependencies. |
| State | state diagram | `[*]`, state names, `-->` with events. |
| Object | object diagram | Instance names and attributes; links. |
| Deployment | deployment diagram | `node`, `artifact`, connections. |
| Timing | timing diagram | Or use sequence with timing. |
| Network | deployment/component | Nodes and links; label protocols. |
| Wireframe | `salt` | Simple UI wireframe elements. |
| Gantt | `gantt` block | Built-in gantt syntax. |
| MindMap | `mindmap` block | Root and branches. |
| WBS | `wbs` block | Work breakdown structure. |
| JSON / YAML | class or object or mindmap | Represent structure; do not output raw JSON/YAML as diagram. |

## Optional Constraints

Use these when the user or context specifies them:

| Constraint | Values | Effect |
|------------|--------|--------|
| **direction** | `LR`, `TB` | LR = left-to-right (good for architecture); TB = top-to-bottom (default for flow). |
| **detail_level** | `low`, `medium`, `high` | Low: fewer nodes/labels. High: more attributes, methods, or messages. |
| **max_nodes** | integer | Cap the number of nodes (e.g. 15, 25, 30). |
| **naming_style** | `DomainFriendly`, `ExactFromPrompt` | Domain-friendly: short, consistent names. Exact: preserve user’s terms. |
| **group_by** | `Layer`, `Domain`, `Service`, `None` | How to group elements in subgraphs/packages. |

Defaults when not specified: `direction` TB (or LR for component/deployment/network); `detail_level` medium; `max_nodes` ~25 (Mermaid) or ~30 (PlantUML).

## PlantUML Stereotypes

Use stereotypes to clarify roles when helpful:

- `<<service>>` – service component  
- `<<db>>` or `<<database>>` – database  
- `<<queue>>` – message queue  
- `<<external>>` – external system  
- `<<interface>>` – interface  

## Mermaid Subgraph Naming

- Use clear, short subgraph IDs and labels: e.g. `subgraph client [Client]`, `subgraph api [API]`, `subgraph db [Database]`.
- Avoid spaces in the ID; use the label in brackets for display.

## Kroki diagram types

The `generate_uml` tool accepts any Kroki backend as `diagram_type`. Use resource `uml://types` for the full list and supported output formats. Summary:

| diagram_type   | Use case / description |
|---------------|-------------------------|
| class, sequence, activity, usecase, state, component, deployment, object | UML via PlantUML (use these or raw `plantuml`) |
| plantuml      | Raw PlantUML (all diagram kinds) |
| mermaid       | Mermaid (sequence, flowchart, classDiagram, gantt, etc.) |
| d2            | D2 diagram scripting language |
| graphviz      | Graphviz (DOT) |
| blockdiag     | Block diagrams (blockdiag family) |
| seqdiag       | Sequence diagrams (blockdiag family) |
| actdiag       | Activity / workflow (blockdiag family) |
| nwdiag        | Network diagrams (blockdiag family) |
| packetdiag    | Packet layout diagrams |
| rackdiag      | Rack / server layout |
| bpmn          | BPMN (Business Process Model and Notation), XML |
| c4plantuml    | C4 model (PlantUML C4) |
| bytefield     | Binary protocol / byte layout |
| dbml          | Database Markup Language schema |
| ditaa         | Diagrams through ASCII art |
| erd            | Entity-relationship diagrams |
| excalidraw    | Excalidraw whiteboard (JSON) |
| nomnoml       | UML-style from shorthand |
| pikchr        | Pikchr diagram scripting |
| structurizr   | Structurizr C4 / architecture DSL |
| svgbob        | ASCII art to SVG |
| symbolator    | Digital logic / schematic symbols |
| tikz          | TikZ/PGF (LaTeX) |
| vega, vegalite| Vega / Vega-Lite visualization (JSON) |
| wavedrom      | Waveform / digital timing |
| wireviz       | Cable / wiring diagrams (YAML) |

## Other Mermaid / Kroki types (reference)

- **User Journey** — Mermaid: represent as flowchart or sequence with user/step nodes.
- **Gitgraph** — Mermaid: `gitGraph` block for commit/branch visualization.
- **ZenUML / Quadrant (XY)** — Kroki supports additional diagram types; map to Mermaid/PlantUML equivalents when needed (e.g. flowchart, sequence).
