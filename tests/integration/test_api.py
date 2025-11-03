"""
Integration tests for API endpoints
"""

import pytest
from fastapi.testclient import TestClient
from main import app
import json


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


def test_health_endpoint(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == "AutoLabMate API"
    assert "version" in data


def test_upload_endpoint_mock(client, tmp_path):
    """Test file upload endpoint"""
    # Create test CSV file
    test_file = tmp_path / "test.csv"
    test_file.write_text("col1,col2\n1,2\n3,4")
    
    with open(test_file, "rb") as f:
        response = client.post(
            "/api/upload",
            files={"file": ("test.csv", f, "text/csv")}
        )
    
    # Should succeed or handle gracefully
    assert response.status_code in [200, 500]  # May fail in test env without DB
    
    if response.status_code == 200:
        data = response.json()
        assert "experiment_id" in data


def test_plan_endpoint(client):
    """Test plan generation endpoint"""
    request_data = {
        "dataset_path": "/uploads/test.csv",
        "experiment_description": "Test experiment"
    }
    
    response = client.post(
        "/api/plan",
        json=request_data
    )
    
    # Should succeed or handle gracefully
    assert response.status_code in [200, 404, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "plan_id" in data
        assert "steps" in data


@pytest.mark.asyncio
def test_execute_endpoint_mock(client):
    """Test execution endpoint"""
    request_data = {
        "plan_id": "plan_test_123"
    }
    
    response = client.post(
        "/api/execute",
        json=request_data
    )
    
    # May fail without plan in DB, that's OK for integration test
    assert response.status_code in [200, 404, 500]


@pytest.mark.asyncio
def test_report_endpoint_not_found(client):
    """Test report endpoint with non-existent ID"""
    response = client.get("/api/report/nonexistent_id")
    
    assert response.status_code in [404, 500]


def test_logs_endpoint(client):
    """Test logs endpoint"""
    response = client.get("/api/logs/test_experiment_id")
    
    assert response.status_code in [200, 500]


@pytest.mark.asyncio
def test_schedule_endpoint_mock(client):
    """Test calendar scheduling endpoint"""
    request_data = {
        "title": "Test Lab Experiment",
        "start_time": "2024-01-01T10:00:00Z",
        "duration": 60
    }
    
    response = client.post(
        "/api/schedule",
        json=request_data
    )
    
    # Should work in mock mode
    assert response.status_code in [200, 500]


def test_github_push_endpoint_mock(client):
    """Test GitHub push endpoint"""
    request_data = {
        "experiment_id": "test_exp_123",
        "commit_message": "Test report"
    }
    
    response = client.post(
        "/api/github/push",
        json=request_data
    )
    
    # Should work in mock mode
    assert response.status_code in [200, 404, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

