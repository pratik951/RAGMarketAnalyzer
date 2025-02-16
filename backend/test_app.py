from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "RAG-Powered Market Research Analysis" in response.text

def test_query():
    response = client.post("/api/query", json={"query": "Test query"})
    assert response.status_code == 200
    assert "insight" in response.json()

def test_compare():
    response = client.post("/api/compare", json={"report1": "Report 1", "report2": "Report 2"})
    assert response.status_code == 200
    assert "comparison" in response.json()