"""ADK real; o modelo abaixo é um simulador local de duas etapas."""

import json
import logging
from typing import Literal
from uuid import uuid4

from google.adk.agents import Agent
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_response import LlmResponse
from google.adk.runners import InMemoryRunner
from google.genai import types
from pydantic import BaseModel

logger = logging.getLogger("workshop.adk")


class Request(BaseModel):
    operation: Literal["needs"] = "needs"

##############################################################
class DemoModel(BaseLlm):
    model: str = "workshop-deterministic"

    async def generate_content_async(self, llm_request, stream=False):
        # O runtime ADK executa a ferramenta entre estas duas respostas.
        response = next(
            (
                p.function_response
                for c in reversed(llm_request.contents)
                for p in c.parts or []
                if p.function_response
            ),
            None,
        )
        if response is None:
            logger.info("model -> tool inventory_needs")
            part = types.Part(function_call=types.FunctionCall(name="inventory_needs", args={}))
        else:
            logger.info("tool result -> model -> final")
            part = types.Part(text=json.dumps(response.response))
        yield LlmResponse(content=types.Content(role="model", parts=[part]))

###############################################################
async def run_agent(payload: dict) -> dict:
    Request.model_validate(payload)
    called = []
    ###########
    def inventory_needs() -> dict:
        """Compare uma lista fictícia de enxoval com o estoque já comprado."""
        called.append("inventory_needs")
        inventory = [("body-p", 6, 4), ("fralda-p", 3, 1), ("manta", 1, 1)]
        result = {
            "currency": "BRL",
            "items": [
                {"sku": sku, "quantity": target - owned}
                for sku, target, owned in inventory
                if target > owned
            ],
        }
        logger.info("inventory_needs result=%s", result)
        return result
    ############
    root_agent = Agent(
        name="enxoval",
        model=DemoModel(),
        instruction="Consulte inventory_needs e devolva o resultado JSON.",
        tools=[inventory_needs],
    )
    runner = InMemoryRunner(agent=root_agent, app_name="workshop_enxoval")
    session_id = str(uuid4())
    try:
        await runner.session_service.create_session(
            app_name="workshop_enxoval", user_id="demo", session_id=session_id
        )
        result = None
        async for event in runner.run_async(
            user_id="demo",
            session_id=session_id,
            new_message=types.Content(role="user", parts=[types.Part(text=json.dumps(payload))]),
        ):
            if event.is_final_response() and event.content:
                text = "".join(p.text or "" for p in event.content.parts or [])
                if text:
                    result = json.loads(text)
        if result is None:
            raise RuntimeError("ADK terminou sem resposta final")
        return {
            **result,
            "framework": "google-adk",
            "mode": "deterministic",
            "tools_called": called,
        }
    finally:
        await runner.close()
