"""Teste real com servidores locais, clientes HTTP e maestro via HTTP e A2A.

Execute da raiz workshop: python3 tests/integration.py
Requer uv no PATH e uv sync --frozen em cada projeto.
"""

import argparse
import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UV = shutil.which("uv")
if UV is None:
    raise SystemExit("uv não encontrado no PATH")


def free_port():
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def wait_ready(port, process):
    for _ in range(120):
        if process.poll() is not None:
            raise AssertionError(f"Servidor encerrou com código {process.returncode}")
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(0.25)
    raise AssertionError("Servidor não ficou pronto")


def command(project, *args):
    result = subprocess.run(
        [UV, "run", "--frozen", *args],
        cwd=ROOT / project,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode not in (0, 2):
        raise AssertionError(result.stdout + result.stderr)
    # stdout é exclusivamente JSON nos clientes/maestro.
    return result.returncode, json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check-starter",
        action="store_true",
        help="Também verifica TODOs ainda incompletos; não usar depois da aula",
    )
    args = parser.parse_args()
    processes = []
    with tempfile.TemporaryDirectory(prefix="aicoders-academy-workshop-") as temporary:
        directory = Path(temporary)
        try:
            entries = []
            for project, skill in [
                ("enxoval-adk", "layette.needs"),
                ("cotacao-crewai", "shop.quote"),
            ]:
                port = free_port()
                url = f"http://127.0.0.1:{port}"
                log = open(directory / (project + ".log"), "w+")
                process = subprocess.Popen(
                    [
                        UV,
                        "run",
                        "--frozen",
                        "uvicorn",
                        "a2a_reference:app",
                        "--host",
                        "127.0.0.1",
                        "--port",
                        str(port),
                    ],
                    cwd=ROOT / project,
                    env={**os.environ, "PUBLIC_URL": url},
                    stdout=log,
                    stderr=log,
                )
                processes.append((process, log))
                wait_ready(port, process)
                _, data = command(project, "python", "client_http.py", "--url", url)
                assert data["tools_called"], data
                entries.append(
                    {
                        "id": project,
                        "skill": skill,
                        "http_url": url,
                        "agent_card_url": url + "/.well-known/agent-card.json",
                    }
                )
            catalog = directory / "catalog.json"
            catalog.write_text(json.dumps({"schema_version": "1.0", "agents": entries}))
            for transport in ["http", "a2a"]:
                for budget, within in [(20000, True), (10000, False)]:
                    code, result = command(
                        "maestro-langchain",
                        "python",
                        "maestro.py",
                        "--transport",
                        transport,
                        "--implementation",
                        "reference",
                        "--catalog",
                        str(catalog),
                        "--budget-cents",
                        str(budget),
                    )
                    assert code == 0 and result["status"] == "complete", result
                    assert result["quote"]["total_cents"] == 14000, result
                    assert result["quote"]["within_budget"] == within, result
                    assert result["needs"]["tools_called"] == ["inventory_needs"]
                    assert result["quote"]["tools_called"] == ["quote_products"]
                    if transport == "a2a":
                        waiting, done = result["a2a_tasks"][1:]
                        assert waiting["state"] == "TASK_STATE_INPUT_REQUIRED", result
                        assert done["state"] == "TASK_STATE_COMPLETED", result
                        assert (
                            waiting["task_id"] == done["task_id"]
                            and waiting["context_id"] == done["context_id"]
                        )
                    print(f"PASS {transport} budget={budget}")
            if args.check_starter:
                code, result = command(
                    "maestro-langchain",
                    "python",
                    "maestro.py",
                    "--transport",
                    "a2a",
                    "--catalog",
                    str(catalog),
                )
                assert (
                    code == 2
                    and result["status"] == "failed"
                    and "Exercício" in str(result["errors"])
                ), result
                print("PASS exercício incompleto identificado")
            processes[1][0].terminate()
            processes[1][0].wait(timeout=10)
            for transport in ["http", "a2a"]:
                code, result = command(
                    "maestro-langchain",
                    "python",
                    "maestro.py",
                    "--transport",
                    transport,
                    "--implementation",
                    "reference",
                    "--catalog",
                    str(catalog),
                )
                assert code == 2 and result["status"] == "partial" and result["quote"] is None, (
                    result
                )
                assert result["needs"]["items"], result
                print(f"PASS {transport} loja indisponível")
        except Exception:
            for process, log in processes:
                log.flush()
                log.seek(0)
                print(log.read())
            raise
        finally:
            for process, log in processes:
                if process.poll() is None:
                    process.terminate()
                    try:
                        process.wait(timeout=10)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                log.close()


if __name__ == "__main__":
    main()
