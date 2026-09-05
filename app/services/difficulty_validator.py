import logging
from typing import List, Dict, Any

from app.llm.client import OllamaClient
from app.llm.prompts import PromptBuilder
from app.schemas.llm_schemas import LLMDifficultyBatch

logger = logging.getLogger(__name__)

class DifficultyValidator:
    """Validates if the generated variations match the seed difficulty."""
    
    def __init__(self, llm_client: OllamaClient):
        self.llm_client = llm_client
        
    async def validate(self, seed_difficulty: str, variations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate difficulty of variations and flag those that deviate too much."""
        if not variations:
            return variations
            
        try:
            prompt = PromptBuilder.build_difficulty_scoring_prompt(seed_difficulty, variations)
            schema = LLMDifficultyBatch.model_json_schema()
            raw_json = await self.llm_client.generate_structured(prompt, schema, temperature=0.0)
            batch = LLMDifficultyBatch.model_validate_json(raw_json)
            
            score_map = {item.variation_index: item.difficulty_level for item in batch.scores}
            
            seed_score = self._difficulty_to_numeric(seed_difficulty)
            
            for i, variation in enumerate(variations):
                scored_diff = score_map.get(i)
                if scored_diff:
                    num_score = self._difficulty_to_numeric(scored_diff)
                    if abs(num_score - seed_score) > 1.5:
                        variation['flagged_for_review'] = True
                else:
                    logger.debug(f"No difficulty score found for variation index {i}")
                    
        except Exception as e:
            logger.warning(f"Difficulty validation failed: {e}. Proceeding without flags.")
            
        return variations

    def _difficulty_to_numeric(self, level: str) -> float:
        """Map difficulty string to a numeric value."""
        level = level.lower()
        mapping = {
            'easy': 1.0,
            'beginner': 1.0,
            'medium': 3.0,
            'intermediate': 3.0,
            'hard': 5.0,
            'advanced': 5.0
        }
        return mapping.get(level, 3.0)

    def _numeric_to_difficulty(self, score: float) -> str:
        """Map numeric score back to difficulty string."""
        if score < 2.0:
            return 'easy'
        elif score < 4.0:
            return 'medium'
        else:
            return 'hard'
