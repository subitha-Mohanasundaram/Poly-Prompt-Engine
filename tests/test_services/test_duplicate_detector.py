import pytest
from app.services.duplicate_detector import DuplicateDetector
from app.utils.embeddings import EmbeddingService

@pytest.fixture
def detector():
    embedding_service = EmbeddingService()
    return DuplicateDetector(embedding_service=embedding_service, threshold=0.85)

def test_identical_texts_detected_as_duplicates(detector):
    seed = "What is the capital of France?"
    variations = [
        "What is the capital city of France?",
        "What is the capital of France?",
        "Explain the theory of general relativity."
    ]
    duplicates, dup_rate = detector.detect(seed, variations)
    assert len(duplicates) >= 1
    assert dup_rate > 0.0

def test_different_texts_not_duplicates(detector):
    seed = "What is the capital of France?"
    variations = [
        "Explain the theory of relativity in simple terms.",
        "How do you solve a quadratic equation using the formula?",
        "What are the main functions of a human liver?"
    ]
    duplicates, dup_rate = detector.detect(seed, variations)
    assert len(duplicates) == 0
    assert dup_rate == 0.0
