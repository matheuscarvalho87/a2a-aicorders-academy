"""EXERCÍCIO: exponha o agente existente sem alterar agent.py ou app.py.

Execute: uv run uvicorn a2a_exercise:app --port 8101 --reload
Antes de implementar, esse comando falha explicitamente. O starter HTTP funciona.
"""

from agent import run_agent
from app import app


def enable_a2a():
    # TODO 1: AgentCard com URL pública, skill layette.needs, JSONRPC e versão 1.0.
    # TODO 2: Executor(AgentExecutor) com execute e cancel.
    # TODO 3: Publicar Task WORKING, extrair DataPart e await run_agent(payload).
    # TODO 4: Publicar artifact com resultado, concluir task; rejeitar entrada inválida.
    # TODO 5: DefaultRequestHandler + InMemoryTaskStore.
    # TODO 6: Montar create_agent_card_routes e create_jsonrpc_routes em app.router.routes.
    raise NotImplementedError("Exercício A2A do ADK; solução em a2a_reference.py")


enable_a2a()
