import pytest

def test_generate_requires_seed_question(test_client):
    response = test_client.post("/api/v1/generate", json={"domain": "mathematics", "count": 5})
    assert response.status_code == 422

def test_generate_validates_domain(test_client):
    response = test_client.post("/api/v1/generate", json={"seed_question": "What is x when 2x=4?", "domain": "invalid_domain", "count": 5})
    assert response.status_code == 422

def test_generate_validates_count_range(test_client):
    response = test_client.post("/api/v1/generate", json={"seed_question": "What is x when 2x=4?", "domain": "mathematics", "count": 1000})
    assert response.status_code == 422
