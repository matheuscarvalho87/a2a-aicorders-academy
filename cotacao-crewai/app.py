import logging

from agent import Request, run_agent
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Cotação · CrewAI · HTTP starter")


@app.get("/health")
def health():
    return {"status": "ok", "framework": "crewai", "mode": "deterministic"}


@app.post("/invoke")
def invoke(request: Request):
    # Handler sync: FastAPI usa threadpool, sem bloquear o loop ASGI.
    return run_agent(request.model_dump())
