import asyncio
import pytest
from app.services.hallucination_detector import HallucinationDetector
from app.utils.embeddings import EmbeddingService

@pytest.fixture
def detector():
    embedding_service = EmbeddingService()
    return HallucinationDetector(
        embedding_service=embedding_service,
        llm_client=None,
        threshold=0.85
    )

def test_evaluate_batch_groundedness(detector):
    seed = "What is the capital of France?"
    variations = [
        {"question": "What is the capital city of France?", "answer_key": "Paris"},
        {"question": "How do you construct a nuclear reactor core?", "answer_key": "Uranium rods"}
    ]
    
    results = asyncio.run(detector.evaluate_batch(seed, "geography", variations))
    
    assert len(results) == 2
    assert "reliability_score" in results[0]
    assert "hallucination_flag" in results[0]
    assert results[0]["reliability_score"] >= 0.85
    assert results[0]["hallucination_flag"] == False
