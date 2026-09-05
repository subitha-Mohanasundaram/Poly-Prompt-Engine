from app.llm.prompts import PromptBuilder
from app.schemas.llm_schemas import LLMSeedAnalysis

def test_seed_analysis_prompt_contains_question():
    q = "What is Python?"
    prompt = PromptBuilder.build_seed_analysis_prompt(q, "programming")
    assert q in prompt
    assert "programming" in prompt

def test_variation_prompt_contains_domain():
    domain = "programming"
    analysis = LLMSeedAnalysis(
        detected_topic="Python",
        detected_subtopic="Basics",
        detected_difficulty="easy",
        detected_question_type="mcq",
        key_concepts=["variables"],
        numerical_values=[],
        context_description="Basic syntax"
    )
    prompt = PromptBuilder.build_variation_prompt("What is Python?", domain, analysis, 5, 0)
    assert domain in prompt
    assert "5" in prompt
