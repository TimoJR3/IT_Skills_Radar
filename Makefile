PYTHON := python3

.PHONY: install run-api run-dashboard test lint up down init-db seed-db

install:
	cp -n .env.example .env || true
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -r requirements.txt

run-api:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-dashboard:
	streamlit run dashboard/app.py

test:
	pytest -q

up:
	cp -n .env.example .env || true
	docker compose up --build

down:
	docker compose down

init-db:
	docker compose exec -T db sh -lc 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -f /docker-entrypoint-initdb.d/01_init_schema.sql'

seed-db:
	docker compose exec -T db sh -lc 'psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB" -f /docker-entrypoint-initdb.d/02_seed_data.sql'
