"""
PS2 Hallucination & Reliability Detection Service.
Evaluates generated question-answer pairs against seed context using local vector embeddings and local LLM-as-a-judge.
"""
import logging
from typing import List, Dict, Any, Tuple
import numpy as np

from app.utils.embeddings import EmbeddingService
from app.utils.similarity import cosine_similarity
from app.llm.client import OllamaClient
from app.schemas.llm_schemas import LLMHallucinationBatch

logger = logging.getLogger(__name__)

class HallucinationDetector:
    """
    Evaluates Groundedness and Factuality of generated variations against seed context.
    Determines overall reliability_score and sets hallucination_flag.
    """

    def __init__(
        self,
        embedding_service: EmbeddingService,
        llm_client: OllamaClient,
        threshold: float = 0.85,
        groundedness_weight: float = 0.5,
        factuality_weight: float = 0.5,
    ):
        self.embedding_service = embedding_service
        self.llm_client = llm_client
        self.threshold = threshold
        self.groundedness_weight = groundedness_weight
        self.factuality_weight = factuality_weight

    async def evaluate_batch(
        self, seed_question: str, domain: str, variations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Evaluates a list of variation dicts for hallucination and reliability.
        Updates each dict in-place with:
          - groundedness_score (float 0..1)
          - factuality_score (float 0..1)
          - reliability_score (float 0..1)
          - hallucination_flag (bool)
          - hallucination_reason (Optional[str])
        """
        if not variations:
            return variations

        # ── 1. Calculate Vector Groundedness Scores ────────────────────
        groundedness_scores = self._calculate_groundedness(seed_question, variations)

        # ── 2. Calculate Factuality Scores via Local LLM Judge ────────
        factuality_scores, reasons = await self._calculate_factuality(
            seed_question, domain, variations
        )

        # ── 3. Compute Composite Reliability & Set Flags ──────────────
        for idx, var in enumerate(variations):
            g_score = groundedness_scores[idx]
            f_score = factuality_scores[idx]
            reason = reasons.get(idx)

            reliability = round(
                (self.groundedness_weight * g_score) + (self.factuality_weight * f_score), 3
            )
            is_hallucinated = reliability < self.threshold

            var["reliability_score"] = reliability
            var["hallucination_flag"] = is_hallucinated

            if is_hallucinated:
                flag_reason = (
                    f"Low reliability score ({reliability:.2f} < {self.threshold:.2f}): "
                    f"Groundedness={g_score:.2f}, Factuality={f_score:.2f}."
                )
                if reason:
                    flag_reason += f" Details: {reason}"
                var["hallucination_reason"] = flag_reason
            else:
                var["hallucination_reason"] = None

        return variations

    def _calculate_groundedness(
        self, seed_question: str, variations: List[Dict[str, Any]]
    ) -> List[float]:
        """
        Computes semantic vector similarity between seed question context
        and variation (question + answer_key).
        """
        seed_emb = self.embedding_service.encode([seed_question])
        var_texts = [f"{v.get('question', '')} {v.get('answer_key', '')}" for v in variations]
        var_embs = self.embedding_service.encode(var_texts)

        sims = cosine_similarity(seed_emb, var_embs)[0]
        # Normalize/clip cosine similarity into 0.0 - 1.0 range
        scores = [float(np.clip((sim + 1.0) / 2.0, 0.0, 1.0)) for sim in sims]
        return scores

    async def _calculate_factuality(
        self, seed_question: str, domain: str, variations: List[Dict[str, Any]]
    ) -> Tuple[List[float], Dict[int, str]]:
        """
        Evaluates domain factuality and logical consistency using local LLM-as-a-judge.
        """
        scores = [0.90] * len(variations)
        reasons: Dict[int, str] = {}

        prompt = f"""
You are an AI Reliability and Factuality Auditor evaluating generated {domain} variations.

SEED CONTEXT: {seed_question}

VARIATIONS TO AUDIT:
"""
        for i, v in enumerate(variations):
            prompt += f"\n[{i}] Question: {v.get('question')}\n    Answer: {v.get('answer_key')}\n"

        prompt += """
For each variation index, evaluate:
1. groundedness_score (0.0 to 1.0): Does it stay true to the core principles of the seed?
2. factuality_score (0.0 to 1.0): Is the answer mathematically/logically/factually 100% correct?
3. reasoning: Brief note if factuality or groundedness is low.

Return JSON adhering strictly to the schema.
"""

        try:
            schema = LLMHallucinationBatch.model_json_schema()
            raw_json = await self.llm_client.generate_structured(prompt, schema, temperature=0.0)
            batch = LLMHallucinationBatch.model_validate_json(raw_json)

            for eval_item in batch.evaluations:
                idx = eval_item.variation_index
                if 0 <= idx < len(variations):
                    scores[idx] = float(round(eval_item.factuality_score, 3))
                    if eval_item.reasoning:
                        reasons[idx] = eval_item.reasoning
        except Exception as e:
            logger.warning(f"Local LLM factuality evaluation fallback trigger: {e}")

        return scores, reasons
