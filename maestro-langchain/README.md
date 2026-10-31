# Maestro · LangChain

Projeto independente, Python 3.12 e uv. O `create_agent` executa um loop com duas ferramentas remotas. O modelo de demonstração escolhe as ferramentas por regras; sem LLM remoto ou chave.

Com os dois especialistas já disponíveis nas portas 8101 e 8102:

```bash
uv sync --frozen
uv run python maestro.py --transport http
uv run pytest -q
```

Com os especialistas executando `a2a_reference:app`:

```bash
uv run python maestro.py --transport a2a --implementation reference
uv run python maestro.py --transport a2a --implementation reference --budget-cents 10000
```

Para usar sua implementação de aula: `uv run python maestro.py --transport a2a`. O default é `--implementation exercise`; os TODOs estão em `client_a2a_exercise.py`. A referência completa está em `client_a2a_reference.py`. O cliente usa apenas SDK A2A/httpx; não importa ADK ou CrewAI.

`catalog.local.json` aponta para localhost. Use `--catalog caminho.json` para trocar os endereços. No Docker, `CATALOG_PATH` seleciona `catalog.docker.json`. O campo `skill` do arquivo é uma convenção exclusiva do starter HTTP; no modo A2A, as skills são lidas das cards dos agentes.

Saída JSON inclui resultado, chamadas de ferramentas e IDs de tarefas A2A. Logs vão para stderr. Códigos de saída: 0 = completo, 2 = parcial/falha de especialista, 1 = configuração inválida. O orçamento padrão é R$ 200,00; a retomada da task que pede orçamento é automática com esse valor. Não há prompt interativo nesta etapa.
