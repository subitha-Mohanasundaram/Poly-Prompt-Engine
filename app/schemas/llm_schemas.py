"""
LLM schemas for structured output generation.
"""
from pydantic import BaseModel, Field
from typing import List, Optional

class LLMVariation(BaseModel):
    question: str
    answer_key: str
    difficulty: str
    question_type: str
    topic: str
    subtopic: str

class LLMVariationBatch(BaseModel):
    variations: List[LLMVariation]

class LLMSeedAnalysis(BaseModel):
    detected_topic: str
    detected_subtopic: str
    detected_difficulty: str
    detected_question_type: str
    key_concepts: List[str]
    numerical_values: List[str]
    context_description: str

class LLMDifficultyScore(BaseModel):
    variation_index: int
    difficulty_level: str
    numeric_score: float
    reasoning: str

class LLMDifficultyBatch(BaseModel):
    scores: List[LLMDifficultyScore]

# PS2 Hallucination Evaluation Schemas
class LLMHallucinationScore(BaseModel):
    variation_index: int
    groundedness_score: float = Field(..., ge=0.0, le=1.0)
    factuality_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: Optional[str] = None

class LLMHallucinationBatch(BaseModel):
    evaluations: List[LLMHallucinationScore]
