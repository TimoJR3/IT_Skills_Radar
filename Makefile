PYTHON ?= python

.PHONY: install check test run-api run-dashboard up down prepare-demo init-db init-analytics seed-db ingest-json ingest-csv dry-run-json generate-large-sample ingest-large-sample load-test-10k

install:
	cp -n .env.example .env || true
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

run-api:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-dashboard:
	streamlit run dashboard/app.py

test:
	$(PYTHON) -m pytest -q

check:
	$(PYTHON) -m compileall app dashboard tests
	$(PYTHON) -m pytest -q

up:
	cp -n .env.example .env || true
	docker compose up --build -d

down:
	docker compose down

init-db:
	docker compose exec -T db sh -lc 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -f /docker-entrypoint-initdb.d/01_init_schema.sql'

prepare-demo:
	docker compose exec -T api python -m app.db.prepare_demo

init-analytics:
	docker compose exec -T db sh -lc 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -f /docker-entrypoint-initdb.d/03_analytics_views.sql'

seed-db:
	docker compose exec -T db sh -lc 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -f /docker-entrypoint-initdb.d/02_seed_data.sql'

ingest-json:
	docker compose exec api python -m app.services.ingestion --input data/samples/prepared_vacancies.json --source manual

ingest-csv:
	docker compose exec api python -m app.services.ingestion --input data/samples/prepared_vacancies.csv --source manual

dry-run-json:
	docker compose exec api python -m app.services.ingestion --input data/samples/prepared_vacancies.json --source manual --dry-run

generate-large-sample:
	$(PYTHON) -m app.services.large_sample --rows 10000 --output data/generated/large_vacancies_10000.json

ingest-large-sample:
	docker compose exec api python -m app.services.ingestion --input data/generated/large_vacancies_10000.json --source manual

load-test-10k: generate-large-sample ingest-large-sample
