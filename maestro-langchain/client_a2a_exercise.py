"""PONTO DE AULA: implemente aqui sem alterar o maestro ou os agentes."""


async def discover(http, card_url: str):
    # TODO 1: GET na URL da Agent Card e raise_for_status().
    # TODO 2: ParseDict(response.json(), AgentCard()) e validar skills/interfaces.
    raise NotImplementedError("Exercício: descobrir Agent Card; veja ../EXERCICIOS.md")


async def send(http, card, payload: dict, previous=None):
    # TODO 3: ClientFactory(ClientConfig(streaming=False, httpx_client=http)).create(card).
    # TODO 4: Message com novo messageId, ROLE_USER e DataPart(payload).
    # TODO 5: Se previous existe, manter taskId/contextId e enviar nova mensagem.
    # TODO 6: Enviar SendMessageRequest e extrair Task e DataPart do artifact.
    # TODO 7: Fechar client em finally. Retornar (task, data).
    raise NotImplementedError("Exercício: consumir A2A; referência em client_a2a_reference.py")
