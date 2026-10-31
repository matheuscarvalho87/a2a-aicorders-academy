from fastapi.testclient import TestClient


def test_crewai_executes_quote_tool():
    from app import app

    with TestClient(app) as client:
        response = client.post(
            "/invoke",
            json={
                "items": [
                    {"sku": "body-p", "quantity": 2},
                    {"sku": "fralda-p", "quantity": 2},
                ],
                "budget_cents": 10000,
            },
        )
    assert response.status_code == 200
    result = response.json()
    assert result["framework"] == "crewai"
    assert result["tools_called"] == ["quote_products"]
    assert result["total_cents"] == 14000
    assert result["within_budget"] is False


def test_unknown_product_does_not_get_a_price():
    from app import app

    with TestClient(app) as client:
        response = client.post(
            "/invoke",
            json={"items": [{"sku": "unknown", "quantity": 1}], "budget_cents": 0},
        )
    assert response.json()["unavailable"] == ["unknown"]
    assert response.json()["offers"] == []


def test_fractional_and_boolean_quantities_rejected():
    from app import app

    with TestClient(app) as client:
        for quantity in (1.5, True, "2"):
            response = client.post(
                "/invoke",
                json={
                    "items": [{"sku": "body-p", "quantity": quantity}],
                    "budget_cents": 10000,
                },
            )
            assert response.status_code == 422
