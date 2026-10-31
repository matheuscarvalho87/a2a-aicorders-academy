# Especialista de cotação · CrewAI

Projeto independente, Python 3.12 e uv. Modelo ReAct determinístico sem API key; o CrewAI executa `quote_products` e devolve a observação da ferramenta.

```bash
uv sync --frozen
uv run uvicorn app:app --port 8102 --reload
```

Em outro terminal nesta pasta:

```bash
uv run python client_http.py
uv run python client_http.py --budget-cents 10000
uv run pytest -q
```

API: GET `/health`, POST `/invoke`, documentação em http://localhost:8102/docs. Pedido: `{"items":[{"sku":"body-p","quantity":2}],"budget_cents":20000}`. Dinheiro em centavos inteiros; preços fictícios. SKUs desconhecidos ficam em `unavailable` e não recebem preço. `within_budget` considera as ofertas disponíveis.

Para o exercício A2A: pare o servidor e use `uv run uvicorn a2a_exercise:app --port 8102 --reload`. Há TODOs explícitos. Solução executável: `uv run uvicorn a2a_reference:app --port 8102 --reload`. A referência preserva `/invoke`, adiciona `/.well-known/agent-card.json` e `/a2a` e expõe a skill `shop.quote`.

Por A2A, pedido válido sem orçamento retorna `INPUT_REQUIRED`. A retomada deve reenviar os itens, acrescentar `budget_cents` e manter task/context. A referência usa o SDK A2A oficial na fronteira, sem depender do adaptador nativo do CrewAI. O framework trabalha dentro de `run_agent` em ambos os transportes.
