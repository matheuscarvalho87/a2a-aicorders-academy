# Especialista de enxoval · Google ADK

Projeto independente, Python 3.12 e uv. Modelo determinístico sem API key; o Runner ADK executa a ferramenta `inventory_needs` de verdade.

```bash
uv sync --frozen
uv run uvicorn app:app --port 8101 --reload
```

Em outro terminal nesta pasta:

```bash
uv run python client_http.py
uv run pytest -q
```

API: GET `/health`, POST `/invoke` com `{"operation":"needs"}`; documentação em http://localhost:8101/docs. Resultado: dois bodies P e dois pacotes de fraldas P, todos fictícios.

Para o exercício A2A: pare o servidor e use `uv run uvicorn a2a_exercise:app --port 8101 --reload`. O arquivo contém TODOs e falha explicitamente enquanto incompleto. Solução executável: `uv run uvicorn a2a_reference:app --port 8101 --reload`. A referência preserva `/invoke`, adiciona `/.well-known/agent-card.json` e `/a2a` e expõe a skill `layette.needs`.

`agent.py` contém o agente, a ferramenta e o modelo simulado. `app.py` contém apenas a API HTTP. O cliente não importa o código do agente. A referência usa o SDK A2A oficial para ensinar o mesmo adaptador nos dois frameworks; o recurso nativo `to_a2a` do ADK é outra opção, fora do exercício principal.
