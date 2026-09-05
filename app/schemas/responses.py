"""
Response schemas for Poly Prompt Engine (PS8 + PS2).
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from app.models.domain import DomainType

class Variation(BaseModel):
    id: int
    question: str
    answer_key: str
    difficulty: str
    question_type: str
    topic: str
    subtopic: str
    confidence_score: float = Field(..., ge=0, le=1)
    flagged_for_review: bool
    # PS2 Hallucination & Reliability Metrics
    reliability_score: float = Field(default=1.0, ge=0, le=1)
    hallucination_flag: bool = Field(default=False)
    hallucination_reason: Optional[str] = Field(default=None)

class GenerateResponse(BaseModel):
    seed_question: str
    domain: DomainType
    total_generated: int
    duplicate_rate: float
    variations: List[Variation]
    review_queue: List[Variation]
    job_id: str

class DomainInfo(BaseModel):
    name: str
    label: str
    description: str
    supported_question_types: List[str]
    topics: Dict[str, List[str]]

class DomainsResponse(BaseModel):
    domains: List[DomainInfo]

class HealthResponse(BaseModel):
    status: Literal['healthy', 'degraded', 'unhealthy']
    ollama_connected: bool
    model_loaded: str
    embedding_model_loaded: bool
    version: str

class ExportResponse(BaseModel):
    job_id: str
    format: Literal['csv', 'json']
    content: str
    filename: str
