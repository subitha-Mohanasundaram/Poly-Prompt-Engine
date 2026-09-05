def test_health_endpoint_returns_200(test_client):
    response = test_client.get("/api/v1/health")
    assert response.status_code == 200

def test_health_response_structure(test_client):
    response = test_client.get("/api/v1/health")
    data = response.json()
    assert "status" in data
    assert "ollama_connected" in data
    assert "embedding_model_loaded" in data
    assert "version" in data
