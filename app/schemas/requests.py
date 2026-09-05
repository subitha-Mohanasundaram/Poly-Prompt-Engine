"""
Request schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal
from app.models.domain import DomainType, QuestionType

class GenerateRequest(BaseModel):
    seed_question: str = Field(..., min_length=10, max_length=2000, description="The initial seed question to generate variations from.")
    domain: DomainType = Field(..., description="The domain of the question.")
    count: int = Field(default=10, ge=1, le=60, description="Number of variations to generate.")
    question_type: Optional[QuestionType] = Field(default=None, description="Type of question to generate. If not provided, it will be auto-detected.")

class ExportRequest(BaseModel):
    job_id: str = Field(..., description="The ID of the generation job to export.")
    format: Literal['csv', 'json'] = Field(default='json', description="Format to export.")
