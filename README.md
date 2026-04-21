# IT Skills Radar

`IT Skills Radar` — portfolio-проект для российского рынка вакансий в data/product-направлениях. Цель сервиса — собирать вакансии, хранить их в PostgreSQL, нормализовывать навыки и затем строить аналитику по спросу на навыки, различиям между ролями и salary premium.

Сейчас в репозитории реализованы:
- FastAPI backend с `/health`
- Streamlit dashboard-заглушка
- PostgreSQL в Docker Compose
- стартовая схема данных под вакансии и навыки
- seed-данные для локальной проверки
- базовые тесты и документация

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
├── docs
├── sql
├── tests
├── .env.example
├── .gitignore
├── Dockerfile
├── Makefile
├── docker-compose.yml
├── README.md
└── requirements.txt
```

## Быстрый старт

### Вариант 1: локально

1. Создать `.env`:

```bash
cp .env.example .env
```

2. Установить зависимости:

```bash
make install
```

3. Запустить API:

```bash
make run-api
```

4. В другом терминале запустить dashboard:

```bash
make run-dashboard
```

5. Прогнать тесты:

```bash
make test
```

### Вариант 2: через Docker Compose

```bash
cp .env.example .env
make up
```

При первом запуске Postgres автоматически применит SQL из папки `sql/`.

Доступные сервисы:
- API: [http://localhost:8000](http://localhost:8000)
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- Dashboard: [http://localhost:8501](http://localhost:8501)

Остановить сервисы:

```bash
make down
```

## Ручная инициализация БД

Если контейнер БД уже был создан раньше и нужно повторно применить схему или сиды:

```bash
make init-db
make seed-db
```

## Текущий scope

Уже сделано:
- каркас репозитория
- конфигурация приложения
- backend entrypoint
- dashboard-заглушка
- dockerized local environment
- слой хранения для вакансий, ролей, навыков и зарплат
- документация по архитектуре и data dictionary

Пока не сделано:
- ingestion вакансий
- миграции
- очистка и нормализация raw-данных
- аналитические витрины и агрегаты
- графики и API аналитики

## Следующий этап

Следующим логичным шагом будет ingestion:
- выбрать 1-2 источника вакансий по РФ-рынку
- сохранять raw payload в БД
- выделять и нормализовывать поля вакансии
- начать загружать навыки и привязывать их к вакансиям
