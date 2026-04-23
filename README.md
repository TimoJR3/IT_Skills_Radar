# IT Skills Radar

`IT Skills Radar` — портфельный проект для анализа спроса на навыки в data и product вакансиях.

Проект показывает полный путь данных:
- загрузка вакансий из prepared source;
- валидация и rule-based нормализация;
- хранение в PostgreSQL;
- аналитические витрины в SQL;
- FastAPI API;
- Streamlit dashboard на русском языке.

## Что умеет проект

Сервис помогает ответить на вопросы:
- какие навыки чаще всего встречаются;
- как меняется спрос на навыки по времени;
- какие навыки характерны для разных ролей;
- какие навыки связаны с более высокой зарплатой;
- как выглядит срез junior / intern ролей.

## Технологический стек

- Python 3.11
- PostgreSQL
- FastAPI
- Streamlit
- Docker Compose
- pytest
- GitHub Actions

## Архитектура

Коротко:

1. `ingestion` читает prepared JSON / CSV.
2. `normalization` очищает поля и приводит роли/навыки к каноническому виду.
3. PostgreSQL хранит raw и final слой.
4. SQL views формируют аналитические витрины.
5. FastAPI отдает агрегаты через API.
6. Streamlit визуализирует результат.

Подробно:
- [docs/architecture.md](</C:/считай что диск D/Pet_project/IT_Skills_Radar/docs/architecture.md:1>)
- [docs/data_dictionary.md](</C:/считай что диск D/Pet_project/IT_Skills_Radar/docs/data_dictionary.md:1>)
- [docs/decisions.md](</C:/считай что диск D/Pet_project/IT_Skills_Radar/docs/decisions.md:1>)
- [docs/analytics.md](</C:/считай что диск D/Pet_project/IT_Skills_Radar/docs/analytics.md:1>)

## Структура репозитория

```text
.
├── .github/workflows
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
├── .dockerignore
├── .env.example
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pytest.ini
├── README.md
└── requirements.txt
```

## Быстрый запуск через Docker

### 1. Перейти в папку проекта

```powershell
cd "C:\считай что диск D\Pet_project\IT_Skills_Radar"
```

### 2. Создать `.env`

```powershell
Copy-Item .env.example .env
```

### 3. Поднять контейнеры

```powershell
docker compose up --build -d
```

### 4. Применить схему и аналитические view

```powershell
make init-db
make init-analytics
make seed-db
```

### 5. Запустить ingestion

Проверка без записи:

```powershell
docker compose exec api python -m app.services.ingestion --input data/samples/prepared_vacancies.json --source manual --dry-run
```

Загрузка prepared sources:

```powershell
docker compose exec api python -m app.services.ingestion --input data/samples/prepared_vacancies.json --source manual
docker compose exec api python -m app.services.ingestion --input data/samples/prepared_vacancies.csv --source manual
```

### 6. Открыть интерфейсы

- API: [http://localhost:8000](http://localhost:8000)
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- Dashboard: [http://localhost:8501](http://localhost:8501)

## Локальный запуск без Docker

Этот вариант подходит, если PostgreSQL уже доступен отдельно и настроен `DATABASE_URL`.

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

## Основные API endpoints

- `GET /health`
- `GET /roles`
- `GET /skills/top`
- `GET /skills/trends`
- `GET /salary/premium`
- `GET /overview/junior`

## Что считается заранее, а что делает API

Заранее считается в PostgreSQL:
- `top_skills_by_role`
- `skills_trend_monthly`
- `role_skill_distribution`
- `skill_salary_premium`
- `junior_roles_overview`

Что делает FastAPI:
- отдает список ролей для фильтров;
- возвращает уже готовые агрегаты с фильтрами;
- предоставляет `/health`.

Что делает Streamlit:
- отправляет запросы в API;
- показывает summary, таблицы и графики;
- не пересчитывает аналитику самостоятельно.

## Тесты и проверки

Локально:

```powershell
py -3 -m compileall app dashboard tests
py -3 -m pytest -q
```

Через Makefile:

```powershell
make check
```

CI:
- GitHub Actions запускает установку зависимостей, compile check и `pytest`.

## Demo-сценарий

Короткий сценарий показа:

1. Открыть dashboard.
2. Выбрать роль `Data Scientist` или `Product Analyst`.
3. Оставить уровни `junior` и `intern`.
4. Показать топ навыков и долю вакансий с ними.
5. Показать динамику одного навыка по времени.
6. Показать salary premium.
7. Завершить срезом по junior / intern ролям.

Подробный чеклист:
- [docs/demo_checklist.md](</C:/считай что диск D/Pet_project/IT_Skills_Radar/docs/demo_checklist.md:1>)

## Документы для портфолио и собеседований

- [docs/resume_bullets.md](</C:/считай что диск D/Pet_project/IT_Skills_Radar/docs/resume_bullets.md:1>)
- [docs/interview_story.md](</C:/считай что диск D/Pet_project/IT_Skills_Radar/docs/interview_story.md:1>)

## Ограничения текущей версии

- ingestion работает с prepared source, а не с live API источников;
- нормализация ролей и навыков rule-based;
- salary premium — это практичная аналитическая метрика, а не causal inference;
- проект intentionally не перегружен enterprise-инфраструктурой.

## Следующие шаги

Если развивать проект дальше, логичные направления:
- подключение реальных источников вакансий;
- расширение нормализации навыков и title aliases;
- обогащение аналитики по локациям и форматам работы;
- планировщик регулярного обновления данных;
- финальная polish-версия UI.
