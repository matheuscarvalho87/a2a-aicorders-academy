"""Cliente independente: não importa CrewAI nem a implementação do agente."""

import argparse
import json

import httpx

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8102")
    parser.add_argument("--budget-cents", type=int, default=20000)
    args = parser.parse_args()
    response = httpx.post(
        args.url + "/invoke",
        json={
            "items": [
                {"sku": "body-p", "quantity": 2},
                {"sku": "fralda-p", "quantity": 2},
            ],
            "budget_cents": args.budget_cents,
        },
        timeout=30,
    )
    response.raise_for_status()
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
