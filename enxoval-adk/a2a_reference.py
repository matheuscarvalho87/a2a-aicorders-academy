"""REFERÊNCIA COMPLETA: adaptador A2A 1.0 reutilizando o agente HTTP existente.

Escolhemos o SDK oficial para tornar explícita a fronteira do protocolo.
O ADK também oferece to_a2a(); este exercício ensina um adaptador universal.
"""

import logging
import os
from uuid import uuid4

from a2a.server.agent_execution import AgentExecutor
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types.a2a_pb2 import AgentCard, Message, Part, Task
from agent import run_agent
from app import app
from google.protobuf.json_format import MessageToDict, ParseDict
from pydantic import ValidationError

logger = logging.getLogger("workshop.a2a")


def agent_message(text):
    return ParseDict(
        {"messageId": str(uuid4()), "role": "ROLE_AGENT", "parts": [{"text": text}]},
        Message(),
    )


class Executor(AgentExecutor):
    async def execute(self, context, event_queue):
        updater = TaskUpdater(event_queue, context.task_id, context.context_id)
        if context.current_task is None:
            await event_queue.enqueue_event(
                ParseDict(
                    {
                        "id": context.task_id,
                        "contextId": context.context_id,
                        "status": {"state": "TASK_STATE_WORKING"},
                    },
                    Task(),
                )
            )
        else:
            await updater.start_work()
        try:
            payload = next(
                MessageToDict(p)["data"] for p in context.message.parts if p.HasField("data")
            )
            result = await run_agent(payload)
            await updater.add_artifact(
                [ParseDict({"data": result}, Part())],
                artifact_id="needs",
                name="Itens faltantes",
            )
            await updater.complete()
            logger.info("task=%s context=%s completed", context.task_id, context.context_id)
        except (ValidationError, StopIteration):
            await updater.reject(agent_message('Envie DataPart com {"operation":"needs"}.'))
        except Exception:
            logger.exception("Falha na execução do agente")
            await updater.failed(
                agent_message("Erro interno ao executar o agente. Consulte os logs.")
            )

    async def cancel(self, context, event_queue):
        await TaskUpdater(event_queue, context.task_id, context.context_id).cancel()


card = ParseDict(
    {
        "name": "Enxoval · Google ADK",
        "description": "Enxoval fictício com modelo determinístico",
        "version": "1.0.0",
        "supportedInterfaces": [
            {
                "url": os.getenv("PUBLIC_URL", "http://localhost:8101") + "/a2a",
                "protocolBinding": "JSONRPC",
                "protocolVersion": "1.0",
            }
        ],
        "capabilities": {},
        "defaultInputModes": ["application/json"],
        "defaultOutputModes": ["application/json"],
        "skills": [
            {
                "id": "layette.needs",
                "name": "Itens faltantes",
                "description": "Compare o estoque com uma lista fictícia de enxoval",
                "tags": ["enxoval"],
            }
        ],
    },
    AgentCard(),
)
handler = DefaultRequestHandler(
    agent_executor=Executor(), task_store=InMemoryTaskStore(), agent_card=card
)
app.router.routes.extend(create_agent_card_routes(card))
app.router.routes.extend(create_jsonrpc_routes(handler, "/a2a"))
