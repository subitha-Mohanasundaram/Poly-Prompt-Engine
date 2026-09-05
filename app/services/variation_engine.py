"""
Core variation generation engine — orchestrates the full PS8 + PS2 pipeline.
"""
import asyncio
import logging
import math
import uuid
from typing import List, Optional

from app.config import Settings
from app.llm.client import OllamaClient
from app.llm.prompts import PromptBuilder
from app.schemas.requests import GenerateRequest
from app.schemas.responses import GenerateResponse, Variation
from app.schemas.llm_schemas import LLMVariation, LLMVariationBatch, LLMSeedAnalysis
from app.services.question_parser import QuestionParser
from app.services.answer_generator import AnswerGenerator
from app.services.duplicate_detector import DuplicateDetector
from app.services.difficulty_validator import DifficultyValidator
from app.services.review_queue import ReviewQueueService
from app.services.hallucination_detector import HallucinationDetector

logger = logging.getLogger(__name__)


class VariationEngine:
    """Main orchestrator for generating question variations with PS8 + PS2 integration."""

    def __init__(
        self,
        llm_client: OllamaClient,
        duplicate_detector: DuplicateDetector,
        difficulty_validator: DifficultyValidator,
        review_queue_service: ReviewQueueService,
        settings: Settings,
        hallucination_detector: Optional[HallucinationDetector] = None,
    ):
        self.llm_client = llm_client
        self.duplicate_detector = duplicate_detector
        self.difficulty_validator = difficulty_validator
        self.review_queue_service = review_queue_service
        self.settings = settings
        self.hallucination_detector = hallucination_detector

        self.parser = QuestionParser(llm_client)
        self.answer_generator = AnswerGenerator(llm_client)

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        """Full pipeline for generating question variations and scoring reliability."""
        job_id = str(uuid.uuid4())
        logger.info(f"Job {job_id}: Starting generation of {request.count} variations.")

        # ── 1. Parse seed question ──────────────────────────────────────
        analysis = await self.parser.parse(request.seed_question, request.domain)
        logger.info(
            f"Job {job_id}: Seed analysis — topic={analysis.detected_topic}, "
            f"difficulty={analysis.detected_difficulty}, type={analysis.detected_question_type}"
        )

        # ── 2. Calculate batches ────────────────────────────────────────
        batch_size = min(self.settings.batch_size, request.count)
        num_batches = math.ceil(request.count / batch_size)
        schema = LLMVariationBatch.model_json_schema()

        # ── 3. Fire all batch LLM calls concurrently ────────────────────
        tasks = []
        for i in range(num_batches):
            remaining = request.count - i * batch_size
            current_batch = min(batch_size, remaining)
            prompt = PromptBuilder.build_variation_prompt(
                request.seed_question, request.domain, analysis, current_batch, i
            )
            tasks.append(self._generate_batch(prompt, schema))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # ── 4. Collect raw LLM variations ───────────────────────────────
        all_llm_variations: List[LLMVariation] = []
        for idx, res in enumerate(results):
            if isinstance(res, list):
                all_llm_variations.extend(res)
            else:
                logger.error(f"Job {job_id}: Batch {idx} failed: {res}")

        all_llm_variations = all_llm_variations[: request.count]
        logger.info(f"Job {job_id}: Collected {len(all_llm_variations)} raw variations.")

        # ── 5. Verify / generate answer keys ────────────────────────────
        verified = await self.answer_generator.verify_answers(
            all_llm_variations, request.domain
        )

        # ── 6. Convert to Variation response objects ────────────────────
        variations: List[Variation] = []
        for idx, (var, confidence) in enumerate(verified):
            variations.append(
                Variation(
                    id=idx + 1,
                    question=var.question,
                    answer_key=var.answer_key,
                    difficulty=var.difficulty,
                    question_type=var.question_type,
                    topic=var.topic,
                    subtopic=var.subtopic,
                    confidence_score=round(confidence, 3),
                    flagged_for_review=False,
                    reliability_score=1.0,
                    hallucination_flag=False,
                    hallucination_reason=None,
                )
            )

        # ── 7. Difficulty validation ────────────────────────────────────
        variation_dicts = [v.model_dump() for v in variations]
        validated_dicts = await self.difficulty_validator.validate(
            analysis.detected_difficulty, variation_dicts
        )
        for i, vd in enumerate(validated_dicts):
            if vd.get("flagged_for_review"):
                variations[i].flagged_for_review = True
                variations[i].confidence_score = round(
                    variations[i].confidence_score * 0.7, 3
                )

        # ── 8. PS2 Hallucination & Reliability Detection ────────────────
        if self.hallucination_detector:
            variation_dicts_for_h = [v.model_dump() for v in variations]
            evaluated_dicts = await self.hallucination_detector.evaluate_batch(
                request.seed_question, request.domain, variation_dicts_for_h
            )
            for i, ed in enumerate(evaluated_dicts):
                variations[i].reliability_score = ed.get("reliability_score", 1.0)
                variations[i].hallucination_flag = ed.get("hallucination_flag", False)
                variations[i].hallucination_reason = ed.get("hallucination_reason", None)

        # ── 9. Duplicate detection ──────────────────────────────────────
        question_texts = [v.question for v in variations]
        dup_indices, duplicate_rate = self.duplicate_detector.detect(
            request.seed_question, question_texts
        )
        logger.info(
            f"Job {job_id}: Duplicate rate = {duplicate_rate:.2%} "
            f"({len(dup_indices)} duplicates)"
        )

        if dup_indices:
            dup_set = set(dup_indices)
            variations = [v for i, v in enumerate(variations) if i not in dup_set]
            for i, v in enumerate(variations):
                v.id = i + 1

        # ── 10. Regeneration if duplicate rate too high ─────────────────
        max_regen_rounds = 2
        regen_round = 0
        while duplicate_rate > 0.10 and regen_round < max_regen_rounds:
            regen_round += 1
            needed = request.count - len(variations)
            if needed <= 0:
                break
            logger.info(
                f"Job {job_id}: Regen round {regen_round} — need {needed} replacements"
            )
            prompt = PromptBuilder.build_variation_prompt(
                request.seed_question,
                request.domain,
                analysis,
                needed,
                num_batches + regen_round,
            )
            new_vars = await self._generate_batch(prompt, schema)
            for var in new_vars:
                idx = len(variations) + 1
                variations.append(
                    Variation(
                        id=idx,
                        question=var.question,
                        answer_key=var.answer_key,
                        difficulty=var.difficulty,
                        question_type=var.question_type,
                        topic=var.topic,
                        subtopic=var.subtopic,
                        confidence_score=0.85,
                        flagged_for_review=False,
                        reliability_score=0.90,
                        hallucination_flag=False,
                        hallucination_reason=None,
                    )
                )
            question_texts = [v.question for v in variations]
            dup_indices, duplicate_rate = self.duplicate_detector.detect(
                request.seed_question, question_texts
            )

        # ── 11. Build review queue (includes PS2 hallucination flags) ────
        borderline = self.duplicate_detector.get_borderline_indices(
            request.seed_question, [v.question for v in variations]
        )
        review_queue = self.review_queue_service.build_queue(variations, borderline)

        # ── 12. Build response ──────────────────────────────────────────
        return GenerateResponse(
            seed_question=request.seed_question,
            domain=request.domain,
            total_generated=len(variations),
            duplicate_rate=round(duplicate_rate, 4),
            variations=variations,
            review_queue=review_queue,
            job_id=job_id,
        )

    async def _generate_batch(
        self, prompt: str, schema: dict
    ) -> List[LLMVariation]:
        """Single batch LLM call with retry on parse failures."""
        for attempt in range(self.settings.max_retries):
            try:
                raw_json = await self.llm_client.generate_structured(prompt, schema)
                batch = LLMVariationBatch.model_validate_json(raw_json)
                return batch.variations
            except Exception as e:
                logger.warning(
                    f"Batch parse attempt {attempt + 1}/{self.settings.max_retries} "
                    f"failed: {e}"
                )
                if attempt == self.settings.max_retries - 1:
                    return []
        return []
