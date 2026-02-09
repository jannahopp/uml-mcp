"""
Pydantic schemas for MCP tool inputs and outputs.
"""

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class GenerateDiagramInput(BaseModel):
    """Input model for diagram generation tools."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    code: str = Field(
        ...,
        description="PlantUML/Mermaid/D2/diagram code (e.g. '@startuml\\nclass User\\n@enduml')",
        min_length=1,
    )
    output_dir: Optional[str] = Field(
        default=None,
        description="Directory to save the generated image (e.g. './output')",
    )
    output_format: str = Field(
        default="svg",
        description="Output format: svg, png, or pdf (depending on diagram type)",
    )
    theme: Optional[str] = Field(
        default=None,
        description="PlantUML theme for UML diagrams (e.g. cerulean, sketchy-outline)",
    )

    @field_validator("code")
    @classmethod
    def validate_code_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Diagram code cannot be empty")
        return v.strip()

    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in ("svg", "png", "pdf"):
            raise ValueError("output_format must be one of: svg, png, pdf")
        return v


class GenerateUMLInput(BaseModel):
    """Input model for generate_uml tool."""

    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    diagram_type: str = Field(
        ...,
        description="Type of diagram (e.g. class, sequence, activity, mermaid, d2)",
        min_length=1,
    )
    code: str = Field(
        ...,
        description="Diagram code in the format for the chosen type",
        min_length=1,
    )
    output_dir: Optional[str] = Field(
        default=None,
        description="Directory to save the generated image",
    )
    output_format: str = Field(
        default="svg",
        description="Output format: svg, png, or pdf",
    )
    theme: Optional[str] = Field(
        default=None,
        description="PlantUML theme (only for PlantUML diagram types)",
    )

    @field_validator("code")
    @classmethod
    def validate_code_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Diagram code cannot be empty")
        return v.strip()

    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        v = v.lower().strip()
        if v not in ("svg", "png", "pdf"):
            raise ValueError("output_format must be one of: svg, png, pdf")
        return v


class DiagramResult(BaseModel):
    """Structured output for diagram generation tools."""

    code: str
    url: Optional[str] = None
    playground: Optional[str] = None
    local_path: Optional[str] = None
    error: Optional[str] = None
