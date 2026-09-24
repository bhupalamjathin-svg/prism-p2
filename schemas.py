from typing import Optional, List
from pydantic import BaseModel, Field


class UnderstandingResult(BaseModel):
    status: str

    domain: Optional[str] = None
    symptom: Optional[str] = None
    canonical_id: Optional[str] = None

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    clarification_needed: bool = False

    question: Optional[str] = None

    options: List[str] = []
