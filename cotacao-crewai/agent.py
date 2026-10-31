"""CrewAI real com modelo ReAct determinístico: tool -> observation -> final."""

import json
import logging
import os
from typing import Annotated

# Configuradas antes de importar CrewAI; a aula não precisa enviar telemetria.
os.environ.setdefault("CREWAI_TELEMETRY_DISABLED", "true")
os.environ.setdefault("OTEL_SDK_DISABLED", "true")
from crewai import Agent, Crew, Task
from crewai.llms.base_llm import BaseLLM
from crewai.tools import tool
from pydantic import BaseModel, BeforeValidator, Field

logger = logging.getLogger("workshop.crewai")


def integer_number(value):
    # Struct/Protobuf pode transformar JSON 2 em Python 2.0.
    if type(value) not in (int, float) or not float(value).is_integer():
        raise ValueError("Esperado número inteiro JSON")
    return int(value)


JsonInteger = Annotated[int, BeforeValidator(integer_number)]


class Item(BaseModel):
    sku: str = Field(min_length=1)
    quantity: JsonInteger = Field(gt=0, le=100)


class Request(BaseModel):
    items: list[Item] = Field(max_length=100)
    budget_cents: JsonInteger = Field(ge=0)


class DemoModel(BaseLLM):
    model: str = "workshop-deterministic"
    request_json: str

    def supports_function_calling(self):
        return False

    def call(self, messages, **kwargs):
        text = (
            messages
            if isinstance(messages, str)
            else "\n".join(str(m.get("content", "")) for m in messages)
        )
        marker = "Observation: "
        for observation in reversed(text.split(marker)[1:]):
            # O prompt ReAct também descreve "Observation:" nas instruções.
            # Só uma observação com o JSON da ferramenta conclui o fluxo.
            try:
                result, _ = json.JSONDecoder().raw_decode(observation.lstrip())
            except ValueError:
                continue
            if isinstance(result, dict) and "total_cents" in result:
                logger.info("observation -> model -> final")
                return "Thought: A ferramenta concluiu a cotação.\nFinal Answer: " + json.dumps(
                    result
                )
        logger.info("model -> tool quote_products")
        return (
            "Thought: Preciso consultar preços fictícios.\nAction: quote_products\nAction Input: "
            + self.request_json
        )


def run_agent(payload: dict) -> dict:
    request = Request.model_validate(payload)
    called = []

    @tool("quote_products")
    def quote_products(items: list[dict], budget_cents: int) -> str:
        """Consulte preços fictícios dos SKUs e compare o total com o orçamento em centavos."""
        normalized = Request(items=items, budget_cents=budget_cents)
        called.append("quote_products")
        prices = {"body-p": 2500, "fralda-p": 4500}
        offers = [
            {"sku": i.sku, "quantity": i.quantity, "unit_price_cents": prices[i.sku]}
            for i in normalized.items
            if i.sku in prices
        ]
        total = sum(i["quantity"] * i["unit_price_cents"] for i in offers)
        result = {
            "currency": "BRL",
            "fictional": True,
            "offers": offers,
            "unavailable": [i.sku for i in normalized.items if i.sku not in prices],
            "total_cents": total,
            "within_budget": total <= normalized.budget_cents,
        }
        logger.info("quote_products result=%s", result)
        return json.dumps(result)

    model = DemoModel(model="workshop-deterministic", request_json=request.model_dump_json())
    specialist = Agent(
        role="Especialista em cotação",
        goal="Consultar preços e respeitar o orçamento",
        backstory="Opera uma loja fictícia para a aula A2A.",
        llm=model,
        tools=[quote_products],
        verbose=False,
        max_iter=3,
        allow_delegation=False,
    )
    task = Task(
        description="Cote os itens deste pedido: " + request.model_dump_json(),
        expected_output="JSON retornado pela ferramenta quote_products.",
        agent=specialist,
    )
    output = Crew(agents=[specialist], tasks=[task], verbose=False, memory=False).kickoff()
    result = json.loads(output.raw)
    if called != ["quote_products"]:
        raise RuntimeError("CrewAI não executou a ferramenta esperada")
    return {
        **result,
        "framework": "crewai",
        "mode": "deterministic",
        "tools_called": called,
    }
