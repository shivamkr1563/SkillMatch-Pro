"""Tests for the API endpoints"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.main import app

client = TestClient(app)


def test_health_check():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()


def test_recommend_valid_query():
    """Test recommendation with valid query"""
    response = client.post(
        "/recommend",
        json={"query": "I need a Java developer with good communication skills"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "query" in data
    assert "recommendations" in data
    assert "count" in data
    assert isinstance(data["recommendations"], list)
    assert data["count"] >= 5
    assert data["count"] <= 10


def test_recommend_empty_query():
    """Test recommendation with empty query"""
    response = client.post(
        "/recommend",
        json={"query": ""}
    )
    assert response.status_code == 422  # Validation error


def test_recommend_short_query():
    """Test recommendation with very short query"""
    response = client.post(
        "/recommend",
        json={"query": "Java"}
    )
    assert response.status_code == 422  # Too short


def test_recommend_response_format():
    """Test recommendation response format"""
    response = client.post(
        "/recommend",
        json={"query": "Looking for sales assessment for new graduates"}
    )
    assert response.status_code == 200
    data = response.json()
    
    # Check response structure
    assert "query" in data
    assert "recommendations" in data
    assert "count" in data
    
    # Check recommendations format
    if data["recommendations"]:
        rec = data["recommendations"][0]
        assert "assessment_name" in rec
        assert "assessment_url" in rec
        assert isinstance(rec["assessment_name"], str)
        assert isinstance(rec["assessment_url"], str)
        assert rec["assessment_url"].startswith("http")


def test_stats_endpoint():
    """Test statistics endpoint"""
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
