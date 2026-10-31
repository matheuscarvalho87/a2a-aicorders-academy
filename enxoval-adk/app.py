import logging

from agent import Request, run_agent
from fastapi import FastAPI

logging.basicConfig(level=logging.INFO)
app = FastAPI(title="Enxoval · Google ADK · HTTP starter")


@app.get("/health")
def health():
    return {"status": "ok", "framework": "google-adk", "mode": "deterministic"}


@app.post("/invoke")
async def invoke(request: Request):
    return await run_agent(request.model_dump())
