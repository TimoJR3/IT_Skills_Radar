# Архитектура проекта

## Общая идея

`IT Skills Radar` построен как небольшой end-to-end data product:
- ingestion читает подготовленные вакансии;
- normalization приводит данные к каноническому виду;
- PostgreSQL хранит raw и final слой;
- аналитические view считают агрегаты;
- FastAPI отдает их через API;
- Streamlit показывает их в dashboard.

## Слои

```text
Prepared source (JSON / CSV)
        |
        v
Ingestion + normalization
        |
        v
PostgreSQL storage
  - raw layer
  - final layer
  - analytics views
        |
        v
FastAPI
        |
        v
Streamlit dashboard
```

## Что за что отвечает

### `app/services/ingestion.py`

Загрузка данных из локального источника, валидация и запись в БД.

### `app/services/normalization.py`

Очистка текста, нормализация ролей, навыков, seniority, зарплат и прочих полей.

### `sql/01_init_schema.sql`

Схема хранения:
- роли;
- вакансии;
- навыки;
- зарплаты;
- raw metadata.

### `sql/03_analytics_views.sql`

Аналитические view:
- `top_skills_by_role`
- `skills_trend_monthly`
- `role_skill_distribution`
- `skill_salary_premium`
- `junior_roles_overview`

### `app/services/analytics.py`

Python-сервис для чтения агрегатов из PostgreSQL.

### `app/api`

FastAPI endpoints и схемы ответов.

### `dashboard`

Русскоязычный Streamlit UI для демонстрации проекта.

### `tests`

Набор unit-тестов и API-тестов.

### `.github/workflows/ci.yml`

CI pipeline:
- устанавливает зависимости;
- проверяет, что Python-файлы компилируются;
- запускает `pytest`.

## Почему архитектура удачная для портфолио

Эта архитектура показывает:
- владение Python beyond notebooks;
- умение проектировать схему данных;
- понимание разницы между raw, cleaned и analytics layer;
- умение разделять SQL, backend и UI;
- умение довести pet-project до состояния, близкого к маленькому продукту.

## Что здесь intentionally упрощено

Архитектура не уходит в enterprise-сложность:
- нет очередей и оркестраторов;
- нет отдельного frontend framework;
- нет внешнего secret management;
- нет сложной миграционной системы.

Это осознанный компромисс: проект остается достаточно сильным для GitHub-портфолио и обсуждения на собеседовании, но не перегружен лишней инфраструктурой.
