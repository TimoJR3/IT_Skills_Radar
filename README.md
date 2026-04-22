# IT Skills Radar

`IT Skills Radar` — портфельный проект по анализу вакансий в data и product направлениях.

Сервис собирает и нормализует вакансии, сохраняет их в PostgreSQL, строит аналитические витрины и показывает:
- какие навыки чаще всего встречаются;
- как меняется спрос на навыки по месяцам;
- чем отличаются роли между собой;
- какие навыки связаны с более высокой зарплатой.

## Что уже реализовано

- слой хранения в PostgreSQL;
- ingestion pipeline из подготовленных JSON и CSV файлов;
- rule-based нормализация ролей и навыков;
- аналитические SQL-витрины;
- FastAPI API поверх агрегатов;
- Streamlit dashboard на русском языке.

## Структура проекта

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

## Как устроен проект

Что считается заранее в PostgreSQL:
- топ навыков по роли;
- динамика навыков по месяцам;
- распределение навыков по ролям;
- salary premium по навыкам;
- обзор junior и intern ролей.

Что делает FastAPI:
- отдает готовые агрегаты из аналитических витрин;
- применяет фильтры по роли, уровню и навыку;
- предоставляет endpoint проверки здоровья `/health`.

Что делает Streamlit:
- показывает фильтры и summary-блок;
- визуализирует топ навыков;
- рисует динамику навыка по времени;
- показывает salary premium и junior overview.

## Быстрый запуск через Docker

### 1. Создать `.env`

PowerShell:

```powershell
Copy-Item .env.example .env
```

### 2. Поднять сервисы

```powershell
docker compose up --build -d
```

### 3. Применить схему, аналитические витрины и seed

```powershell
make init-db
make init-analytics
make seed-db
```

### 4. Запустить ingestion

Сначала безопасная проверка:

```powershell
docker compose exec api python -m app.services.ingestion --input data/samples/prepared_vacancies.json --source manual --dry-run
```

Потом загрузка данных:

```powershell
docker compose exec api python -m app.services.ingestion --input data/samples/prepared_vacancies.json --source manual
docker compose exec api python -m app.services.ingestion --input data/samples/prepared_vacancies.csv --source manual
```

### 5. Открыть интерфейсы

- API: [http://localhost:8000](http://localhost:8000)
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- Dashboard: [http://localhost:8501](http://localhost:8501)

## Локальный запуск без Docker

### 1. Установить зависимости

```powershell
py -3 -m pip install -r requirements.txt
```

### 2. Запустить API

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Запустить dashboard

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

## Пример demo-сценария

На защите проекта можно идти так:

1. Открыть dashboard и показать, что интерфейс строится поверх API.
2. Выбрать роль `Data Scientist` или `Product Analyst`.
3. Оставить уровни `junior` и `intern`.
4. Показать блок топ навыков и объяснить метрику доли вакансий.
5. Выбрать навык `Python` или `SQL` и показать его динамику по времени.
6. Показать блок salary premium и объяснить разницу медианных зарплат.
7. Завершить junior overview как кратким срезом entry-level рынка.

## Полезные команды

```powershell
make test
make ingest-json
make ingest-csv
make dry-run-json
docker compose down
```

## Текущий scope

Уже сделано:
- storage layer;
- ingestion;
- normalization;
- analytics layer;
- API;
- dashboard MVP.

Пока не сделано:
- продвинутые коннекторы внешних источников;
- оркестрация по расписанию;
- полноценная финальная полировка UI;
- финальная CI-конфигурация.
