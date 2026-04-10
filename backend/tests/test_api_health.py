"""Smoke tests for the API bootstrap health endpoint."""

from fastapi.testclient import TestClient

from optimark_athena.app import app


def test_healthcheck_reports_backend_workspace() -> None:
    """Verify the API health endpoint reports the expected bootstrap payload."""
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "app_name": "optimark",
        "service_name": "athena",
        "layer": "api",
        "persistence_provider": "postgres",
        "workspace_packages": ["metis", "mnemosyne", "clio"],
    }
