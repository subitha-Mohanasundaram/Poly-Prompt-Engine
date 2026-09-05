def test_domains_returns_5_domains(test_client):
    response = test_client.get("/api/v1/domains")
    assert response.status_code == 200
    data = response.json()
    assert "domains" in data
    assert len(data["domains"]) == 5

def test_domain_names_are_valid(test_client):
    response = test_client.get("/api/v1/domains")
    data = response.json()
    domain_names = [d["name"] for d in data["domains"]]
    assert "mathematics" in domain_names
    assert "programming" in domain_names
    assert "science" in domain_names
    assert "business" in domain_names
    assert "language" in domain_names

def test_each_domain_has_question_types(test_client):
    response = test_client.get("/api/v1/domains")
    data = response.json()
    for domain in data["domains"]:
        assert "supported_question_types" in domain
        assert isinstance(domain["supported_question_types"], list)
        assert len(domain["supported_question_types"]) > 0
