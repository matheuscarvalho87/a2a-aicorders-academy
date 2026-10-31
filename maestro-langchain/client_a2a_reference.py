"""Cliente SDK A2A 1.0/JSONRPC. Nenhum import do framework dos servidores."""

from uuid import uuid4

from a2a.client import ClientConfig, ClientFactory
from a2a.types.a2a_pb2 import AgentCard, SendMessageRequest
from google.protobuf.json_format import MessageToDict, ParseDict


async def discover(http, card_url: str):
    response = await http.get(card_url)
    response.raise_for_status()
    card = ParseDict(response.json(), AgentCard())
    if not card.supported_interfaces or not card.skills:
        raise ValueError("Agent Card sem interfaces ou skills")
    return card


async def send(http, card, payload: dict, previous=None):
    client = ClientFactory(ClientConfig(streaming=False, httpx_client=http)).create(card)
    message = {
        "messageId": str(uuid4()),
        "role": "ROLE_USER",
        "parts": [{"data": payload}],
    }
    if previous is not None:
        message.update(taskId=previous.id, contextId=previous.context_id)
    request = ParseDict(
        {"message": message, "configuration": {"returnImmediately": False}},
        SendMessageRequest(),
    )
    try:
        async for event in client.send_message(request):
            if event.HasField("task"):
                task = event.task
                data = next(
                    (
                        MessageToDict(p)["data"]
                        for a in task.artifacts
                        for p in a.parts
                        if p.HasField("data")
                    ),
                    None,
                )
                return task, data
        raise ValueError("Resposta A2A sem task")
    finally:
        await client.close()
