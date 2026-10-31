"""Cliente independente: não importa ADK nem a implementação do agente."""

import argparse
import json

import httpx

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8101")
    args = parser.parse_args()
    response = httpx.post(args.url + "/invoke", json={"operation": "needs"}, timeout=30)
    response.raise_for_status()
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
