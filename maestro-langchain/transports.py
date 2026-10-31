"""HTTP próprio no starter; cliente A2A genérico no exercício/referência."""

import asyncio
import importlib
import json
import logging
from pathlib import Path

import httpx

logger = logging.getLogger("workshop.transport")


class RemoteAgents:
    def __init__(self, catalog: Path, transport="http", implementation="exercise"):
        document = json.loads(catalog.read_text())
        if document.get("schema_version") != "1.0" or not document.get("agents"):
            raise ValueError("Catálogo vazio ou versão inválida")
        self.entries = document["agents"]
        ids = [entry["id"] for entry in self.entries]
        if len(ids) != len(set(ids)):
            raise ValueError("IDs duplicados no catálogo")
        self.transport = transport
        self.implementation = implementation
        self.trace = []

    def invoke(self, skill, payload):
        if self.transport == "http":
            # Convenção proprietária: o cliente conhece /invoke e o campo skill.
            matches = [a for a in self.entries if a["skill"] == skill]
            if len(matches) != 1:
                raise ValueError(f"Esperado um agente para {skill}, encontrados {len(matches)}")
            with httpx.Client(timeout=30) as client:
                response = client.post(matches[0]["http_url"] + "/invoke", json=payload)
                response.raise_for_status()
                return response.json()
        return asyncio.run(self._invoke_a2a(skill, payload))

    async def _invoke_a2a(self, skill, payload):
        module = importlib.import_module("client_a2a_" + self.implementation)
        async with httpx.AsyncClient(timeout=30) as http:
            # As skills vêm das cards, não do nome ou framework do fornecedor.
            cards, errors = [], []
            for entry in self.entries:
                try:
                    card = await module.discover(http, entry["agent_card_url"])
                    if any(s.id == skill for s in card.skills):
                        cards.append(card)
                except Exception as error:
                    errors.append(f"{entry['id']}: {error}")
            if len(cards) != 1:
                raise ValueError(
                    f"Esperado um agente A2A para {skill}, encontrados {len(cards)}. {errors}"
                )
            card = cards[0]
            # Demonstração explícita de INPUT_REQUIRED: primeiro não informa orçamento.
            first = {k: v for k, v in payload.items() if k != "budget_cents"}
            task, data = await module.send(http, card, first)
            self._record(card.name, task)
            from a2a.types.a2a_pb2 import TaskState

            if task.status.state == TaskState.TASK_STATE_INPUT_REQUIRED:
                if "budget_cents" not in payload:
                    raise ValueError("Agente pediu informação não disponível")
                previous = task
                task, data = await module.send(http, card, payload, previous=previous)
                if task.id != previous.id or task.context_id != previous.context_id:
                    raise ValueError("Retomada perdeu task/context")
                self._record(card.name, task)
            if task.status.state != TaskState.TASK_STATE_COMPLETED or data is None:
                raise ValueError(f"Agente não completou: {TaskState.Name(task.status.state)}")
            return data

    def _record(self, agent, task):
        from a2a.types.a2a_pb2 import TaskState

        event = {
            "agent": agent,
            "task_id": task.id,
            "context_id": task.context_id,
            "state": TaskState.Name(task.status.state),
        }
        self.trace.append(event)
        logger.info("A2A %s", event)
