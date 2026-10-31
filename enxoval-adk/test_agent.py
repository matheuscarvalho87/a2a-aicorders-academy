from fastapi.testclient import TestClient


def test_adk_executes_inventory_tool():
    from app import app

    with TestClient(app) as client:
        response = client.post("/invoke", json={"operation": "needs"})
    assert response.status_code == 200
    result = response.json()
    assert result["framework"] == "google-adk"
    assert result["tools_called"] == ["inventory_needs"]
    assert result["items"] == [
        {"sku": "body-p", "quantity": 2},
        {"sku": "fralda-p", "quantity": 2},
    ]


def test_http_rejects_unknown_operation():
    from app import app

    with TestClient(app) as client:
        assert client.post("/invoke", json={"operation": "buy"}).status_code == 422
