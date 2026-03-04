from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_docs_endpoint():
    """Basic smoke test verifying that the FastAPI docs are accessible."""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "Swagger UI" in response.text
