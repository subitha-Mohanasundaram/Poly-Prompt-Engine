import pytest
from app.services.difficulty_validator import DifficultyValidator

def test_difficulty_to_numeric_mapping():
    validator = DifficultyValidator(llm_client=None)
    assert validator._difficulty_to_numeric("easy") == 1.0
    assert validator._difficulty_to_numeric("medium") == 3.0
    assert validator._difficulty_to_numeric("hard") == 5.0

def test_numeric_to_difficulty_mapping():
    validator = DifficultyValidator(llm_client=None)
    assert validator._numeric_to_difficulty(1.0) == "easy"
    assert validator._numeric_to_difficulty(3.0) == "medium"
    assert validator._numeric_to_difficulty(5.0) == "hard"
