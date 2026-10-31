import pytest


def test_langchain_routes_tools_and_preserves_partial_result():
    from maestro import orchestrate

    class OfflineShop:
        def invoke(self, skill, payload):
            if skill == "layette.needs":
                return {"currency": "BRL", "items": [{"sku": "body-p", "quantity": 2}]}
            raise ConnectionError("loja indisponível")

    result = orchestrate(OfflineShop(), 20000)
    assert result["status"] == "partial"
    assert result["needs"]["items"][0]["quantity"] == 2
    assert result["quote"] is None
    assert [t["tool"] for t in result["trace"]] == ["identify_needs", "quote_items"]


def test_negative_budget_rejected_before_network():
    from maestro import orchestrate

    with pytest.raises(ValueError):
        orchestrate(None, -1)
