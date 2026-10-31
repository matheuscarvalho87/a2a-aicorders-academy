# Workshop A2A · AI Coders Academy

Transforme agentes independentes em serviços que outros agentes podem descobrir e consumir. O material começa com HTTP funcionando e reserva a exposição/consumo A2A para o código ao vivo.

**É uma demonstração determinística:** modelos e dados são simulados. LangChain, Google ADK, CrewAI, ferramentas, processos e chamadas HTTP/A2A são reais. Não precisa de chave LLM, conta cloud ou plataforma. O projeto não acessa nem procura credenciais no ambiente.

## Estrutura

```text
maestro-langchain/   Cliente coordenador e duas ferramentas remotas
enxoval-adk/        Agente ADK com ferramenta de estoque fictício
cotacao-crewai/     Agente CrewAI com ferramenta de cotação fictícia
EXERCICIOS.md      Passos para implementar A2A durante a aula
TROUBLESHOOTING.md Problemas comuns e recuperação
tests/             Teste de integração com processos reais
```

Cada pasta tem `pyproject.toml`, `uv.lock`, Dockerfile e README próprios. Pode ser copiada e executada separadamente. Use este diretório como raiz do repositório GitHub marcado como **Template repository**. Os locks e as configurações de debug são parte do material dos alunos; ambientes virtuais, caches e material local do apresentador ficam fora do versionamento.

## Início rápido · Docker

No terminal WSL/Linux/macOS, dentro desta pasta. Requer Docker com Compose v2. O build inicial precisa de internet e baixa as dependências Python; faça antes da aula.

```bash
# 1. Starter: dois agentes com API HTTP pronta
docker compose up -d --build --wait
# 2. Cliente maestro LangChain consumindo essas APIs
docker compose run --rm --build maestro --transport http
# 3. Logs dos frameworks e suas ferramentas
docker compose logs -f --tail=30 enxoval cotacao
```

O resultado deve conter `status: complete`, 2 bodies P e 2 pacotes de fraldas P, cotação de `14000` centavos e `within_budget: true` para orçamento de `20000`. Os campos `framework`, `mode` e `tools_called` tornam explícito o que foi executado.

As APIs ficam em http://localhost:8101/docs e http://localhost:8102/docs. Para executar os clientes HTTP isolados:

```bash
docker compose exec enxoval python client_http.py
docker compose exec cotacao python client_http.py
```

Neste starter as Agent Cards e `/a2a` ainda não estão expostas: GET na card retorna 404. As portas 8101/8102 não conflitam com a prova anterior nas portas 8000–8002. Se estiver usando execução uv, pare esses servidores antes de subir os containers nas mesmas portas.

## Referência A2A completa

```bash
# Mesmo projeto Compose e mesmas APIs, agora com A2A habilitado
docker compose -f compose.yaml -f compose.reference.yaml up -d --build --wait
docker compose run --rm --build maestro --transport a2a --implementation reference
# Mesmo preço, orçamento insuficiente
docker compose run --rm maestro --transport a2a --implementation reference --budget-cents 10000
# Inspecionar a card pelo host
curl -s http://localhost:8101/.well-known/agent-card.json | python3 -m json.tool
```

Na saída `a2a_tasks`, a loja passa por `INPUT_REQUIRED` e `COMPLETED` com os mesmos IDs de task/context. O maestro inicialmente omite o orçamento para demonstrar a pausa e o fornece automaticamente na retomada. Não há interação de terminal nesta etapa.

As cards dos containers anunciam DNS Docker; use o maestro pelo Compose. Para depurar com uv e localhost, use os comandos abaixo. `PUBLIC_URL` controla a URL anunciada, não a interface de bind do servidor.

## Codar e depurar localmente · uv

Requer Python 3.12 e [uv](https://docs.astral.sh/uv/getting-started/installation/). `uv sync` pode obter o Python compatível se necessário. Windows: use o terminal Ubuntu/WSL. `--frozen` respeita os locks e não atualiza versões durante a aula.

```bash
cd enxoval-adk
uv sync --frozen
uv run uvicorn app:app --port 8101 --reload
```

Em outro terminal, a partir da raiz do workshop:

```bash
cd cotacao-crewai
uv sync --frozen
uv run uvicorn app:app --port 8102 --reload
```

Em um terceiro terminal:

```bash
cd maestro-langchain
uv sync --frozen
uv run python maestro.py --transport http
```

Os clientes HTTP estão nas pastas dos especialistas: `uv run python client_http.py`. Para A2A, pare os servidores com Ctrl+C e troque `app:app` por `a2a_exercise:app` ou `a2a_reference:app`. O maestro usa `--transport a2a` para o exercício e `--transport a2a --implementation reference` para a solução.

É possível colocar breakpoints em `run_agent`, nas ferramentas e nos adaptadores. Para debug Python com VS Code, selecione a `.venv` do projeto e rode `uvicorn` sem `--reload` no debugger; o reload cria um processo filho.

Também incluímos `workshop.code-workspace`: abra esse arquivo no VS Code conectado ao WSL para carregar as três pastas. Depois de sincronizar os ambientes, as configurações de execução oferecem HTTP, exercício e referência para cada projeto. Escolha uma por especialista, inicie os dois servidores e então execute o maestro. Não execute simultaneamente as três variantes do mesmo servidor, pois usam a mesma porta.

## O que o aluno implementa

- `enxoval-adk/a2a_exercise.py`: Agent Card, executor, artifacts e rotas A2A.
- `cotacao-crewai/a2a_exercise.py`: mesmo adaptador, com pedido de orçamento e retomada da tarefa.
- `maestro-langchain/client_a2a_exercise.py`: descobrir a card e enviar mensagens com o SDK oficial.

As soluções estão em `a2a_reference.py` de cada especialista e `client_a2a_reference.py` do maestro. Elas chamam o mesmo agente usado por `/invoke`; não duplicam a lógica de negócio. Os arquivos incompletos não são importados no starter HTTP.

Para executar os arquivos preenchidos da aula por Docker:

```bash
docker compose -f compose.yaml -f compose.exercise.yaml up -d --build --wait
docker compose run --rm --build maestro --transport a2a --implementation exercise
```

Esse comando falha explicitamente antes de preencher os TODOs. Durante a aula, prefira uv com reload para não reconstruir imagens a cada edição. Os exercícios não modificam automaticamente os arquivos de referência.

## Testes e recuperação

```bash
# Em cada uma das três pastas
uv run --frozen pytest -q
# Na raiz, com uv no PATH e os três ambientes sincronizados
python3 tests/integration.py
# Para verificar também que o template original tem TODOs explícitos
python3 tests/integration.py --check-starter
# Parar apenas os containers deste workshop
docker compose down
```

O teste de integração usa portas temporárias, inicia e limpa seus próprios processos, executa os clientes HTTP e o maestro pelos dois caminhos, testa orçamento menor e loja indisponível. Nenhum serviço da plataforma é necessário. Depois de completar os exercícios, não use `--check-starter`.

Com `make` instalado, há atalhos: `make setup`, `make http`, `make reference`, `make run-http`, `make run-a2a`, `make test`, `make down`.

## Contratos e limites

`POST /invoke` é uma API didática própria. O modo CLI `http` significa essa API; A2A também usa HTTP, com binding JSONRPC e protocolo 1.0. Todos os projetos usam `a2a-sdk==1.3.0` nos locks. Usamos o SDK oficial como adaptador comum para evitar misturar interfaces nativas/versionamentos dos frameworks no exercício principal.

O catálogo é um arquivo local: `catalog.local.json` ou `catalog.docker.json`. No starter, `skill` e `http_url` permitem uma integração particular com `/invoke`. No caminho A2A, o cliente lê `agent_card_url` e encontra as skills nas cards. A plataforma poderá fornecer essas referências depois; ela não participa do fluxo desta etapa.

Agentes expostos separadamente podem ser operados por fornecedores diferentes. Este material demonstra a fronteira de serviço e interoperabilidade. Autenticação, autorização, medição e cobrança por uso são etapas posteriores. Serviços locais ficam no loopback e tarefas A2A ficam em memória. Os dados não são recomendação de saúde nem preços de mercado.

Veja os [exercícios](EXERCICIOS.md) e o [troubleshooting](TROUBLESHOOTING.md).
