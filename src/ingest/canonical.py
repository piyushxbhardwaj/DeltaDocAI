import uuid
from typing import Literal, Optional, Dict, Any, List
from pydantic import BaseModel, Field

ObjectType = Literal[
    "Text",
    "Valve",
    "Instrument",
    "Dimension",
    "Pipeline",
    "Equipment",
    "Annotation",
    "Title Block",
    "Notes"
]

class CanonicalObject(BaseModel):
    """
    Canonical representation of extracted engineering document elements.
    Downstream modules (delta engine, visual diff, RAG) operate on this model.
    """
    id: str = Field(default_factory=lambda: uuid.uuid4().hex)
    type: ObjectType = "Text"
    tag: Optional[str] = None
    text: str
    page: int = 1
    bbox: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])  # [x0, y0, x1, y1]
    rotation: float = 0.0
    layer: str = "0"
    font_size: Optional[float] = None
    confidence: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def is_tagged(self) -> bool:
        return self.tag is not None and len(self.tag.strip()) > 0
