FROM ghcr.io/astral-sh/uv:0.13.0 AS uv
FROM python:3.12-slim
COPY --from=uv /uv /uvx /bin/
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
ENV PATH="/app/.venv/bin:$PATH"
RUN useradd --create-home demo
USER demo
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8101"]
