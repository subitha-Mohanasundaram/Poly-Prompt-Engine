import logging
from app.llm.client import OllamaClient
from app.llm.prompts import PromptBuilder
from app.schemas.llm_schemas import LLMSeedAnalysis

logger = logging.getLogger(__name__)

class QuestionParser:
    """Service to analyze and parse seed questions."""
    
    def __init__(self, llm_client: OllamaClient):
        self.llm_client = llm_client
        
    async def parse(self, seed_question: str, domain: str) -> LLMSeedAnalysis:
        """Parse a seed question to extract structured metadata."""
        prompt = PromptBuilder.build_seed_analysis_prompt(seed_question, domain)
        schema = LLMSeedAnalysis.model_json_schema()
        
        try:
            response_json = await self.llm_client.generate_structured(prompt, schema)
            analysis = LLMSeedAnalysis.model_validate_json(response_json)
            return analysis
        except Exception as e:
            logger.warning(f"LLM parsing failed: {e}. Falling back to heuristic parsing.")
            return self._heuristic_parse(seed_question, domain)
            
    def _heuristic_parse(self, seed_question: str, domain: str) -> LLMSeedAnalysis:
        """Fallback method when LLM fails."""
        q_type = "free_text"
        if "```" in seed_question:
            q_type = "coding"
        elif "A)" in seed_question or "a)" in seed_question:
            q_type = "multiple_choice"
        elif "___" in seed_question:
            q_type = "fill_in_blank"
            
        return LLMSeedAnalysis(
            topic="general",
            subtopic="general",
            difficulty="medium",
            question_type=q_type,
            key_concepts=["general concept"],
            numerical_values=[],
            context_description="Basic heuristic context"
        )
