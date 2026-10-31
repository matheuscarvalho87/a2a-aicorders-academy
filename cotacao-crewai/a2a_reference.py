"""REFERÊNCIA COMPLETA: SDK A2A oficial na fronteira, CrewAI dentro do agente."""

import asyncio
import logging
import os
from uuid import uuid4

from a2a.server.agent_execution import AgentExecutor
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore, TaskUpdater
from a2a.types.a2a_pb2 import AgentCard, Message, Part, Task
from agent import Request, run_agent
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
            if "budget_cents" not in payload:
                Request.model_validate({**payload, "budget_cents": 0})
                await updater.requires_input(
                    agent_message("Informe budget_cents e reenvie items na mesma task/context.")
                )
                return
            # CrewAI é síncrono: não bloquear o event loop do servidor A2A.
            result = await asyncio.to_thread(run_agent, payload)
            await updater.add_artifact(
                [ParseDict({"data": result}, Part())],
                artifact_id="quote",
                name="Cotação fictícia",
            )
            await updater.complete()
            logger.info("task=%s context=%s completed", context.task_id, context.context_id)
        except (ValidationError, StopIteration):
            await updater.reject(
                agent_message("Envie items válidos e budget_cents inteiro não negativo.")
            )
        except Exception:
            logger.exception("Falha na execução do agente")
            await updater.failed(
                agent_message("Erro interno ao executar o agente. Consulte os logs.")
            )

    async def cancel(self, context, event_queue):
        await TaskUpdater(event_queue, context.task_id, context.context_id).cancel()


card = ParseDict(
    {
        "name": "Cotação · CrewAI",
        "description": "Preços fictícios; nenhuma compra é realizada",
        "version": "1.0.0",
        "supportedInterfaces": [
            {
                "url": os.getenv("PUBLIC_URL", "http://localhost:8102") + "/a2a",
                "protocolBinding": "JSONRPC",
                "protocolVersion": "1.0",
            }
        ],
        "capabilities": {},
        "defaultInputModes": ["application/json"],
        "defaultOutputModes": ["application/json"],
        "skills": [
            {
                "id": "shop.quote",
                "name": "Cotar produtos",
                "description": "Consulte preços fictícios e compare com o orçamento",
                "tags": ["cotacao"],
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
