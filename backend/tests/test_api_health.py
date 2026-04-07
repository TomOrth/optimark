from fastapi.testclient import TestClient

from optimark_athena.app import app


def test_healthcheck_reports_backend_workspace() -> None:
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
