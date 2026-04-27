# IT Skills Radar

`IT Skills Radar` — портфельный data-проект, который показывает, какие навыки чаще всего требуются в data/product вакансиях, как меняется спрос по времени и какие навыки связаны с более высокой зарплатой.


## Коротко

Проект демонстрирует полный путь данных от сырого источника до готового интерфейса:

1. загрузка вакансий из подготовленных `JSON/CSV`;
2. валидация и очистка данных;
3. нормализация ролей и навыков;
4. хранение в `PostgreSQL`;
5. аналитические SQL-витрины;
6. `FastAPI` для доступа к агрегатам;
7. `Streamlit` dashboard на русском языке.

Проект intentionally сделан без enterprise-перегруза: простая архитектура, понятный код и воспроизводимый запуск через Docker.

## Что можно узнать

- Какие навыки чаще всего встречаются в вакансиях.
- Какие навыки характерны для `Data Scientist`, `Data Analyst`, `Product Analyst`, `ML Engineer`.
- Как меняется спрос на навыки по месяцам.
- Какие навыки связаны с более высокой медианной зарплатой.
- Как выглядит рынок junior / intern data/product ролей.

## Для кого проект

Для `Data Scientist` проект показывает работу с подготовкой данных, нормализацией, SQL, аналитическими витринами и базовой инженерной упаковкой.

Для `Product / Data Analyst` проект показывает умение переводить бизнес-вопросы в метрики, сегменты, витрины и понятный dashboard.

## Стек

| Слой | Инструменты |
| --- | --- |
| Backend | Python 3.11, FastAPI |
| Data storage | PostgreSQL |
| Analytics | SQL views, Python services |
| Dashboard | Streamlit |
| Infrastructure | Docker Compose |
| Quality | pytest, GitHub Actions |

## Архитектура

```text
Prepared JSON/CSV
      |
      v
Ingestion + validation
      |
      v
Cleaning + rule-based normalization
      |
      v
PostgreSQL: raw + final tables
      |
      v
Analytics SQL views
      |
      v
FastAPI endpoints
      |
      v
Streamlit dashboard
```

Главная идея: тяжелые аналитические расчеты живут в PostgreSQL views, API остается тонким, а dashboard только запрашивает готовые агрегаты.

Подробности:
- [Архитектура](docs/architecture.md)
- [Словарь данных](docs/data_dictionary.md)
- [Решения по нормализации](docs/decisions.md)
- [Описание метрик](docs/analytics.md)

## Быстрый запуск

Требования:
- Docker Desktop
- Docker Compose

```powershell
Copy-Item .env.example .env
docker compose up --build -d
```

Инициализировать базу, витрины и seed-данные:

```powershell
make init-db
make init-analytics
make seed-db
```

Загрузить sample-данные через ingestion pipeline:

```powershell
docker compose exec api python -m app.services.ingestion --input data/samples/prepared_vacancies.json --source manual
docker compose exec api python -m app.services.ingestion --input data/samples/prepared_vacancies.csv --source manual
```

Открыть:
- API: [http://localhost:8000](http://localhost:8000)
- Swagger: [http://localhost:8000/docs](http://localhost:8000/docs)
- Dashboard: [http://localhost:8501](http://localhost:8501)

## Проверка без записи в БД

```powershell
docker compose exec api python -m app.services.ingestion --input data/samples/prepared_vacancies.json --source manual --dry-run
```

## API

| Endpoint | Назначение |
| --- | --- |
| `GET /health` | Проверка доступности API |
| `GET /roles` | Список ролей для фильтров |
| `GET /skills/top` | Топ навыков по роли и уровню |
| `GET /skills/trends` | Динамика навыков по месяцам |
| `GET /salary/premium` | Salary premium по навыкам |
| `GET /overview/junior` | Обзор junior / intern ролей |

## Аналитические витрины

| Витрина | Что показывает |
| --- | --- |
| `analytics.top_skills_by_role` | Самые частые навыки внутри роли |
| `analytics.skills_trend_monthly` | Помесячную динамику спроса |
| `analytics.role_skill_distribution` | Отличия навыков между ролями |
| `analytics.skill_salary_premium` | Разницу медианной зарплаты с навыком и без него |
| `analytics.junior_roles_overview` | Срез по junior / intern вакансиям |

## Структура проекта

```text
IT_Skills_Radar
├── app
│   ├── api
│   ├── core
│   ├── db
│   ├── schemas
│   └── services
├── dashboard
├── data/samples
├── docs
├── sql
├── tests
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── README.md
└── requirements.txt
```

## Тесты

```powershell
py -3 -m compileall app dashboard tests
py -3 -m pytest -q
```

Через Makefile:

```powershell
make check
```

В CI GitHub Actions запускает установку зависимостей, проверку компиляции и `pytest`.

## Demo-сценарий

1. Открыть dashboard.
2. Выбрать роль `Data Scientist` или `Product Analyst`.
3. Оставить уровни `junior` и `intern`.
4. Показать топ навыков и долю вакансий с ними.
5. Выбрать один навык и показать динамику по месяцам.
6. Показать salary premium.
7. Завершить обзором junior / intern ролей.

Подробный чеклист: [docs/demo_checklist.md](docs/demo_checklist.md)

## Что демонстрирует проект

- `Python` для data processing и backend-логики.
- `SQL/PostgreSQL` для хранения данных и аналитических витрин.
- Проектирование простой, но практичной data model.
- Rule-based нормализацию ролей и навыков.
- `FastAPI` для доступа к аналитическим агрегатам.
- `Streamlit` для понятного dashboard.
- `Docker Compose`, `pytest`, `GitHub Actions` для воспроизводимости и качества.

## Документы для собеседования

- [Bullet points для резюме](docs/resume_bullets.md)
- [Interview story](docs/interview_story.md)

## Ограничения

- Источник данных сейчас подготовленный: локальные `JSON/CSV`, без live scraping/API.
- Нормализация ролей и навыков rule-based, без тяжелого NLP.
- Salary premium показывает аналитическую связь, а не причинно-следственный эффект.
- Проект сфокусирован на portfolio-ready MVP, поэтому архитектура оставлена простой.

## Лицензия

Проект распространяется по лицензии [MIT](LICENSE).
