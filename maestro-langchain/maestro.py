"""O LangChain executa o loop e as tools; DemoModel simula as decisões do LLM."""

import argparse
import json
import logging
import os
from pathlib import Path
from uuid import uuid4

from langchain.agents import create_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.tools import tool

logger = logging.getLogger("workshop.maestro")


class DemoModel(BaseChatModel):
    @property
    def _llm_type(self):
        return "workshop-deterministic"

    def bind_tools(self, tools, **kwargs):
        return self

    def _generate(self, messages, stop=None, run_manager=None, **kwargs):
        outputs = {m.name: json.loads(m.content) for m in messages if isinstance(m, ToolMessage)}
        budget = json.loads(next(m.content for m in messages if m.type == "human"))["budget_cents"]
        if "identify_needs" not in outputs:
            name, args = "identify_needs", {}
        elif outputs["identify_needs"]["ok"] and "quote_items" not in outputs:
            name, args = (
                "quote_items",
                {
                    "items": outputs["identify_needs"]["data"]["items"],
                    "budget_cents": budget,
                },
            )
        else:
            needs = outputs.get("identify_needs", {})
            quote = outputs.get("quote_items", {})
            result = {
                "status": "complete"
                if needs.get("ok") and quote.get("ok")
                else ("partial" if needs.get("ok") else "failed"),
                "needs": needs.get("data"),
                "quote": quote.get("data"),
                "errors": [v["error"] for v in outputs.values() if not v["ok"]],
            }
            return ChatResult(
                generations=[ChatGeneration(message=AIMessage(content=json.dumps(result)))]
            )
        logger.info("model -> tool %s args=%s", name, args)
        message = AIMessage(
            content="",
            tool_calls=[{"name": name, "args": args, "id": str(uuid4()), "type": "tool_call"}],
        )
        return ChatResult(generations=[ChatGeneration(message=message)])


def orchestrate(remote, budget_cents: int) -> dict:
    if type(budget_cents) is not int or budget_cents < 0:
        raise ValueError("budget_cents deve ser um inteiro não negativo")
    trace = []

    def execute(tool_name, skill, payload):
        try:
            data = remote.invoke(skill, payload)
            result = {"ok": True, "data": data}
        except Exception as error:
            logger.warning("remote call failed: %s", error)
            result = {"ok": False, "error": str(error)}
        trace.append({"tool": tool_name, "skill": skill, **result})
        return json.dumps(result)

    @tool
    def identify_needs() -> str:
        """Peça ao especialista remoto os itens faltantes no enxoval."""
        return execute("identify_needs", "layette.needs", {"operation": "needs"})

    @tool
    def quote_items(items: list[dict], budget_cents: int) -> str:
        """Peça uma cotação ao especialista remoto para os itens e orçamento informados."""
        return execute("quote_items", "shop.quote", {"items": items, "budget_cents": budget_cents})

    agent = create_agent(
        model=DemoModel(),
        tools=[identify_needs, quote_items],
        system_prompt="Consulte os especialistas e consolide o resultado sem inventar preços.",
    )
    state = agent.invoke(
        {"messages": [{"role": "user", "content": json.dumps({"budget_cents": budget_cents})}]},
        config={"recursion_limit": 10},
    )
    result = json.loads(state["messages"][-1].content)
    return {
        **result,
        "budget_cents": budget_cents,
        "framework": "langchain",
        "mode": "deterministic",
        "trace": trace,
        "a2a_tasks": getattr(remote, "trace", []),
    }


if __name__ == "__main__":
    from transports import RemoteAgents

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("--transport", choices=["http", "a2a"], default="http")
    parser.add_argument("--implementation", choices=["exercise", "reference"], default="exercise")
    parser.add_argument(
        "--catalog",
        type=Path,
        default=Path(os.getenv("CATALOG_PATH", str(Path(__file__).parent / "catalog.local.json"))),
    )
    parser.add_argument("--budget-cents", type=int, default=20000)
    args = parser.parse_args()
    try:
        remote = RemoteAgents(args.catalog, args.transport, args.implementation)
        result = orchestrate(remote, args.budget_cents)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        raise SystemExit(0 if result["status"] == "complete" else 2)
    except (ValueError, OSError) as error:
        parser.exit(1, str(error) + "\n")
