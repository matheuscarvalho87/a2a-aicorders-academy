"""EXERCÍCIO: exponha a cotação CrewAI pelo mesmo contrato A2A.

Execute: uv run uvicorn a2a_exercise:app --port 8102 --reload
Antes de implementar, esse comando falha explicitamente. O starter HTTP funciona.
"""

from agent import Request, run_agent
from app import app


def enable_a2a():
    # TODO 1: AgentCard: skill shop.quote, JSONRPC, versão 1.0, URL pública.
    # TODO 2: Executor: Task WORKING e DataPart do pedido.
    # TODO 3: Sem budget_cents, validar items e retornar INPUT_REQUIRED.
    # TODO 4: Na retomada, atualizar a task existente; não criar um novo ID.
    # TODO 5: await asyncio.to_thread(run_agent, payload), artifact e COMPLETED.
    # TODO 6: Rejeitar entrada inválida; falha interna -> FAILED; implementar cancel.
    # TODO 7: Handler, store e rotas de card/JSONRPC.
    raise NotImplementedError("Exercício A2A do CrewAI; solução em a2a_reference.py")


enable_a2a()
