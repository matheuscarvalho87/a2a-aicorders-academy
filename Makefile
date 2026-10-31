.PHONY: setup http reference exercise run-http run-a2a run-exercise test down
setup:
	cd enxoval-adk && uv sync --frozen
	cd cotacao-crewai && uv sync --frozen
	cd maestro-langchain && uv sync --frozen
http:
	docker compose up -d --build --wait
reference:
	docker compose -f compose.yaml -f compose.reference.yaml up -d --build --wait
exercise:
	docker compose -f compose.yaml -f compose.exercise.yaml up -d --build --wait
run-http:
	docker compose run --rm --build maestro --transport http
run-a2a:
	docker compose run --rm --build maestro --transport a2a --implementation reference
run-exercise:
	docker compose run --rm --build maestro --transport a2a --implementation exercise
test:
	cd enxoval-adk && uv run --frozen pytest -q
	cd cotacao-crewai && uv run --frozen pytest -q
	cd maestro-langchain && uv run --frozen pytest -q
	python3 tests/integration.py
down:
	docker compose down
