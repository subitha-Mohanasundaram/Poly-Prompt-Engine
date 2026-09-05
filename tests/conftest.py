import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def test_client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def sample_generate_request():
    return {
        "seed_question": "What is the derivative of x^2 with respect to x?",
        "domain": "mathematics",
        "count": 5
    }

@pytest.fixture
def sample_variation():
    return {
        "id": 1,
        "question": "Find the first derivative of f(x) = x^2.",
        "answer_key": "2x",
        "difficulty": "medium",
        "question_type": "descriptive",
        "topic": "Calculus",
        "subtopic": "derivatives",
        "confidence_score": 0.95,
        "flagged_for_review": False
    }
