# Problemas comuns

| Sintoma | Verificação/ação |
|---|---|
| Porta ocupada | Pare o servidor uv antes do Docker, ou vice-versa. Workshop usa 8101/8102. |
| Card retorna 404 | Starter `app:app` só publica HTTP. Use módulo de exercício preenchido ou referência. |
| `NotImplementedError` | Esperado no exercício original; preencha TODOs ou selecione a referência. |
| URL `enxoval` não resolve no host | É DNS Docker. Use maestro no Compose; com uv use `catalog.local.json`. |
| Card anuncia localhost dentro do Docker | Configure PUBLIC_URL com nome do serviço e recrie o container. |
| Alteração não aparece | uvicorn com `--reload` na pasta correta ou Compose com `--build`. |
| Cliente A2A não conecta ao HTTP starter | Falta habilitar rotas A2A no servidor. |
| JSON numérico 2.0 no Python | Protobuf Struct usa números de ponto flutuante; schema aceita valores inteiros e rejeita frações/booleanos. |
| Cotação retornou `partial` | Leia `errors`, logs da cotação e `/health`; trace mantém a etapa que funcionou. |
| Orçamento menor e cotação completa | `complete` indica que a consulta concluiu; `within_budget: false` indica que excede o orçamento. |
| Primeiro build demorado | Dependências dos frameworks são maiores. Faça o download antes da aula; locks evitam atualização inesperada. |
| Avisos de depreciação do CrewAI | A versão fixada emite avisos internos; não são chamadas de LLM nem falha de rede. Não atualize durante a aula. |
| Breakpoint não ativa | Selecione a `.venv` do projeto e desative reload ao depurar pelo VS Code. |

Logs: `docker compose logs -f --tail=50 enxoval cotacao`. Código de saída do maestro: 0 sucesso, 2 parcial/falha remota, 1 configuração inválida. Ctrl+C em `logs -f` não para os serviços.

Referências oficiais: [A2A](https://a2a-protocol.org/latest/specification/), [Google ADK](https://adk.dev/a2a/quickstart-exposing/), [CrewAI](https://docs.crewai.com/en/learn/a2a-agent-delegation), [LangChain](https://docs.langchain.com/oss/python/langchain/agents).
