# IT Skills Radar

`IT Skills Radar` is a portfolio project for vacancy analytics in data and product roles.

The project now includes:
- PostgreSQL storage for normalized vacancies, roles, skills and salaries
- ingestion pipeline from prepared JSON and CSV files
- analytics views for top skills, trends, role comparison and salary premium
- FastAPI endpoints over the analytics layer
- Streamlit dashboard connected to the API

## Project structure

```text
.
├── app
│   ├── api
│   ├── core
│   ├── db
│   ├── models
│   ├── schemas
│   ├── services
│   └── main.py
├── dashboard
├── data
│   └── samples
├── docs
├── sql
├── tests
├── .env.example
├── Dockerfile
├── Makefile
├── docker-compose.yml
├── README.md
└── requirements.txt
```

## What is precomputed vs. what comes from API

Precomputed in PostgreSQL views:
- top skills by role
- monthly skills trend
- salary premium by skill
- role skill distribution
- junior and intern overview

Returned by FastAPI:
- filtered rows from those precomputed views
- roles list for UI filters
- health check

Rendered in Streamlit:
- role and seniority filters
- top skills table
- skill trend chart
- salary premium block
- junior summary block

## Quick start with Docker

### 1. Create `.env`

PowerShell:

```powershell
Copy-Item .env.example .env
```

### 2. Start services

```powershell
docker compose up --build -d
```

### 3. Apply schema, analytics views and seed

```powershell
make init-db
make init-analytics
make seed-db
```

### 4. Run ingestion

Dry-run:

```powershell
docker compose exec api python -m app.services.ingestion --input data/samples/prepared_vacancies.json --source manual --dry-run
```

Load JSON:

```powershell
docker compose exec api python -m app.services.ingestion --input data/samples/prepared_vacancies.json --source manual
```

Load CSV:

```powershell
docker compose exec api python -m app.services.ingestion --input data/samples/prepared_vacancies.csv --source manual
```

### 5. Open services

- API: [http://localhost:8000](http://localhost:8000)
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- Dashboard: [http://localhost:8501](http://localhost:8501)

## Local run without Docker

### 1. Install dependencies

```powershell
py -3 -m pip install -r requirements.txt
```

### 2. Start API

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Start dashboard

```powershell
streamlit run dashboard/app.py
```

## API endpoints

- `GET /health`
- `GET /roles`
- `GET /skills/top`
- `GET /skills/trends`
- `GET /salary/premium`
- `GET /overview/junior`

## Demo scenario

One simple project demo flow:

1. Open the dashboard.
2. Select `Data Scientist` or `Product Analyst`.
3. Filter to `junior` and `intern`.
4. Show the top skills block and explain the share metric.
5. Show the trend chart for one selected skill such as `Python` or `SQL`.
6. Show the salary premium block and explain that it compares median salary with and without the skill.
7. Close with the junior overview table to show market snapshot for entry-level roles.

## Useful commands

```powershell
make test
make ingest-json
make ingest-csv
make dry-run-json
docker compose down
```

## Current scope

Already implemented:
- storage model
- ingestion pipeline
- analytics views
- API layer
- dashboard MVP

Not implemented yet:
- production-grade scheduling
- richer source connectors
- auth
- final UI polish
- CI refinement
