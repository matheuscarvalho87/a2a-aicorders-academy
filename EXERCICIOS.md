# Exercícios A2A

Objetivo: expor um agente existente e consumi-lo sem importar seu framework. Não reescreva as ferramentas ou a lógica de negócio.

## Checkpoint 0 · HTTP pronto

Execute os dois `app:app`, os respectivos `client_http.py` e o maestro `--transport http`. Confirme R$ 140,00 e ferramentas dos três frameworks nos logs. O arquivo `agent.py` é fornecido pronto; não é o conteúdo principal de implementação ao vivo.

## Checkpoint 1 · Enxoval A2A

Arquivo: `enxoval-adk/a2a_exercise.py`. Use `a2a_reference.py` apenas se precisar recuperar o checkpoint.

1. Importe `AgentExecutor`, handler/store, tipos protobuf e helpers de rotas do SDK.
2. Crie uma `AgentCard` com `supportedInterfaces`, URL `http://localhost:8101/a2a`, `protocolBinding: JSONRPC`, `protocolVersion: 1.0`, entrada/saída `application/json`, skill `layette.needs` e descrição honesta do mock. Use `PUBLIC_URL` como na referência para Docker.
3. Implemente `execute(context, event_queue)`. Crie uma task com `context.task_id` e `context.context_id`, publique WORKING, extraia o DataPart e invoque `await run_agent(payload)`.
4. Publique o resultado como artifact e mude a task para COMPLETED. Entrada de negócio inválida deve gerar REJECTED; falha de execução, FAILED. Implemente `cancel` com TaskUpdater.
5. Crie `DefaultRequestHandler`, `InMemoryTaskStore` e adicione as rotas de card/JSONRPC ao `app` já existente.

Pare o HTTP e execute `uv run uvicorn a2a_exercise:app --port 8101 --reload`. Valide `curl http://localhost:8101/.well-known/agent-card.json`; `/invoke` deve continuar funcionando. A card é uma descrição do agente; o endpoint `/a2a` executa as operações do protocolo.

## Checkpoint 2 · Cliente do maestro

Arquivo: `maestro-langchain/client_a2a_exercise.py`. Assinaturas já usadas pelo maestro:

```python
async def discover(http, card_url: str):  # -> protobuf AgentCard
    ...


async def send(http, card, payload: dict, previous=None):  # -> (protobuf Task, dict | None)
    ...
```

1. Faça GET na card e valide status. Converta o JSON com `ParseDict(..., AgentCard())`.
2. Use `ClientFactory(ClientConfig(streaming=False, httpx_client=http)).create(card)` para respeitar a interface anunciada.
3. Crie `SendMessageRequest` com `messageId` novo, `ROLE_USER`, DataPart e `returnImmediately: false`.
4. Se `previous` existir, preencha `taskId` e `contextId` com os IDs recebidos; nunca copie o `messageId` da mensagem anterior.
5. Percorra `client.send_message(request)` e extraia a task e o JSON do artifact. INPUT_REQUIRED pode não ter artifact; retorne `None` como dados nesse caso.
6. Feche o client em `finally`. A decisão de retomar com orçamento está pronta em `transports.py`.

Teste inicialmente com a cotação usando a referência para manter o foco no cliente: `uv run uvicorn a2a_reference:app --port 8102 --reload`. No maestro, execute `uv run python maestro.py --transport a2a`. O modo padrão usa o exercício.

## Checkpoint 3 · CrewAI e tarefa com pausa

Arquivo: `cotacao-crewai/a2a_exercise.py`.

Reutilize o padrão do enxoval, trocando a skill para `shop.quote`. Sem orçamento, valide os itens usando o schema do projeto e publique INPUT_REQUIRED. Ao receber a retomada, use o contexto da tarefa existente e publique WORKING via TaskUpdater. Execute `run_agent` em `asyncio.to_thread`, pois o CrewAI fornecido é síncrono. Retorne a cotação em artifact e conclua.

Valide no `a2a_tasks` do maestro:

```text
Enxoval: COMPLETED
Cotação: INPUT_REQUIRED
Cotação: COMPLETED  <- mesmo task_id e context_id da linha anterior
```

O pedido de retomada inclui novamente `items` e acrescenta `budget_cents`. Essa convenção é do nosso caso de negócio; A2A não define o formato universal de um pedido de cotação.

## Checkpoint 4 · Independência dos fornecedores

No catálogo, mude somente `id` e o nome local dos registros: a execução A2A deve continuar funcionando, pois as skills vêm das cards. Trocar uma URL só funciona se o novo servidor estiver acessível e anunciar uma interface válida.

Pare a cotação e rode o maestro: deverá retornar `status: partial`, necessidades preservadas e `quote: null`. Religue e teste `--budget-cents 10000`: mesmo preço e `within_budget: false`. Observe os logs e os IDs de task/context.

## Recuperação rápida

Troque o módulo do servidor para `a2a_reference:app` e use `--implementation reference` no maestro. Isso não sobrescreve o exercício do participante. Volte para `app:app` e `--transport http` para retornar ao início.
