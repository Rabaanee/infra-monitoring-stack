"""
Unit tests for the Deployment Tracker API.

These tests are run:
1. Locally by developers before committing
2. Automatically in the CI pipeline (GitHub Actions)
3. Inside the Docker build (multi-stage build)

3 layers of tests

If ANY test fails, the pipeline stops. This is a quality gate.
"""

import pytest
import json
import sys
import os
from app import app

# Add parent directory to path so we can import app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def client():
    """
    Create a test client for the Flask app.

    WHAT IS A FIXTURE?
    A pytest fixture is setup code that runs before each test.
    The test client lets us make HTTP requests to our app without
    actually starting a server — it's fast and isolated.
    """
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Tests for the /health endpoint — the most critical endpoint in K8s."""

    def test_health_returns_200(self, client):
        """Health check should always return 200 when app is running."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_healthy_status(self, client):
        """Response should include status: healthy."""
        response = client.get("/health")
        data = json.loads(response.data)
        assert data["status"] == "healthy"

    def test_health_includes_version(self, client):
        """Response should include the app version."""
        response = client.get("/health")
        data = json.loads(response.data)
        assert "version" in data

    def test_health_includes_hostname(self, client):
        """Response should include hostname (shows which pod responded)."""
        response = client.get("/health")
        data = json.loads(response.data)
        assert "hostname" in data


class TestDeploymentsEndpoint:
    """Tests for the /api/deployments CRUD endpoints."""

    def test_list_deployments_empty(self, client):
        """Initially, deployment list should be empty."""
        response = client.get("/api/deployments")
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "deployments" in data

    def test_create_deployment(self, client):
        """POST should create a new deployment record."""
        payload = {
            "service": "web-frontend",
            "version": "1.2.0",
            "environment": "dev",
            "deployed_by": "github-actions",
        }
        response = client.post(
            "/api/deployments",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["service"] == "web-frontend"
        assert data["version"] == "1.2.0"
        assert data["status"] == "success"
        assert "timestamp" in data

    def test_create_deployment_with_defaults(self, client):
        """POST with minimal data should use sensible defaults."""
        response = client.post(
            "/api/deployments",
            data=json.dumps({"service": "api-gateway"}),
            content_type="application/json",
        )
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data["version"] == "0.0.0"
        assert data["environment"] == "dev"

    def test_create_deployment_no_body_returns_400(self, client):
        """POST with no JSON body should return 400."""
        response = client.post("/api/deployments", content_type="application/json")
        assert response.status_code == 400


class TestInfoEndpoint:
    """Tests for the /api/info metadata endpoint."""

    def test_info_returns_200(self, client):
        response = client.get("/api/info")
        assert response.status_code == 200

    def test_info_includes_app_name(self, client):
        response = client.get("/api/info")
        data = json.loads(response.data)
        assert data["app"] == "deployment-tracker"


class TestRootEndpoint:
    """Tests for the root / endpoint."""

    def test_root_returns_200(self, client):
        response = client.get("/")
        assert response.status_code == 200

    def test_root_lists_endpoints(self, client):
        response = client.get("/")
        data = json.loads(response.data)
        assert "endpoints" in data
