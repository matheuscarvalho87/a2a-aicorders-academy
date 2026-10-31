FROM ghcr.io/astral-sh/uv:0.13.0 AS uv
FROM python:3.12-slim
COPY --from=uv /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
ENV PATH="/app/.venv/bin:$PATH" CATALOG_PATH=/app/catalog.docker.json
RUN useradd --create-home demo
USER demo
ENTRYPOINT ["python", "maestro.py"]
