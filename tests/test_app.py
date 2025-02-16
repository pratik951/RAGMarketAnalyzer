import pytest
from fastapi.testclient import TestClient
from ..backend.app import app  # Use relative import to import the app module

client = TestClient(app)

def test_query_endpoint():
    response = client.post("/api/query", json={"query": "What is the financial outlook for ConocoPhillips?"})
    assert response.status_code == 200
    assert "insight" in response.json()
    assert "sentiment" in response.json()
    assert "topics" in response.json()

def test_compare_endpoint():
    response = client.post("/api/compare", json={"report1": "Report1", "report2": "Report2"})
    assert response.status_code == 200
    assert "comparison" in response.json()
