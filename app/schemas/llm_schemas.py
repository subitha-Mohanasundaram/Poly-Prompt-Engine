"""
LLM schemas for structured output generation.
"""
from pydantic import BaseModel
from typing import List

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
