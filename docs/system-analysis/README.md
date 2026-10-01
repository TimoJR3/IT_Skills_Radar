# IT Skills Radar — аналитическая документация (системный анализ)

Раздел с документацией системного аналитика: полный комплект аналитических артефактов к проекту
[IT Skills Radar](../../README.md). Код проекта — в корне репозитория, документация — в этой папке.

## О проекте

IT Skills Radar анализирует вакансии junior/intern-уровня в data- и product-аналитике и показывает, какие навыки встречаются чаще всего, как меняется спрос по месяцам и есть ли зарплатный сигнал у навыка.
Данные проходят пайплайн `JSON/CSV → validation → cleaning → normalization → PostgreSQL → SQL views → FastAPI → Streamlit`.
Проект упакован в Docker Compose, покрыт тестами pytest и проверяется в GitHub Actions.

## Статус документации

Код проекта реализован; документация описывает его как системный аналитик — от бизнес-контекста и требований до API-контракта, интеграции и НФТ — и дополняет целевым (TO-BE) состоянием там, где кода пока нет.

## Как отличить реализованное от спроектированного

Документация опирается на реальный код репозитория (`app/api/routes.py`, `app/schemas/analytics.py`, `sql/01_init_schema.sql`, `sql/03_analytics_views.sql`, `app/services/ingestion.py`, `app/services/normalization.py`, `docs/data_dictionary.md`, `docs/decisions.md`).

- Всё, что есть в коде, описано как есть: имена таблиц, полей, витрин, эндпоинтов и параметров совпадают с репозиторием.
- Всё, чего в коде нет, помечено в тексте: **(проектное решение, в текущей реализации отсутствует)**. Это целевое (TO-BE) состояние.

## Навигация по артефактам

| № | Артефакт | Что внутри |
|---|---|---|
| 1 | [Бизнес-контекст](01-business-context.md) | Проблема, цели, стейкхолдеры, границы (in/out of scope), метрики успеха |
| 2 | [Требования](02-requirements.md) | 8 user stories с AC (Given/When/Then), use case UC-01, НФТ с числами, MoSCoW |
| 3 | [Процесс (BPMN)](03-process-bpmn.md) | AS-IS и TO-BE процесса сбора и обновления вакансий: описание + диаграмма со swimlanes |
| 4 | [Модель данных](04-data-model.md) | ER-диаграмма, словарь данных, ограничения, витрины `analytics.*` |
| 5 | [API](05-api.md) + [openapi.yaml](api/openapi.yaml) | OpenAPI 3.0 спецификация, обзор эндпоинтов, примеры запросов/ответов, коды ошибок, problem+json |
| 6 | [Sequence-диаграммы](06-sequence.md) | Загрузка данных, запрос дашборда через API, обработка ошибки валидации |
| 7 | [Интеграция](07-integration.md) | Спецификация интеграции с источником вакансий: событие `vacancy.ingested.v1`, JSON Schema, SLA, идемпотентность, ретраи, DLQ, мониторинг |
| 8 | [НФТ и архитектура](08-nfr-architecture.md) | C4 Context и Container, НФТ, наблюдаемость |
| 9 | [Глоссарий](09-glossary.md) | Термины предметной области и системного анализа |

Рекомендуемый порядок чтения: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8. Глоссарий — по необходимости.

### Трассировка (сквозная логика)

| Цель | User story | Use case / процесс | Данные | API | Sequence |
|---|---|---|---|---|---|
| BG-01 Топ навыков | US-01 | UC-01 | `analytics.top_skills_by_role` | `GET /skills/top` | SD-02 |
| BG-01 Динамика | US-02 | — | `analytics.skills_trend_monthly` | `GET /skills/trends` | — |
| BG-01 Сравнение ролей | US-03 | — | `analytics.role_skill_distribution` | `GET /skills/distribution` (проект) | — |
| BG-02 Зарплатный сигнал | US-04 | — | `analytics.skill_salary_premium` | `GET /salary/premium` | — |
| BG-01 Junior-срез | US-05 | — | `analytics.junior_roles_overview` | `GET /overview/junior` | — |
| BG-03 Идемпотентная загрузка | US-06, US-07 | BPMN AS-IS / TO-BE | `vacancies`, `raw_source_metadata` | CLI `app.services.ingestion`; событие `vacancy.ingested.v1` (проект) | SD-01, SD-03 |
| BG-03 Диагностика стенда | US-08 | — | все витрины | `GET /health` | — |

## Стек исходного проекта

| Слой | Технологии |
|---|---|
| Backend | Python 3.11, FastAPI, SQLAlchemy, Pydantic |
| База данных | PostgreSQL 16 |
| Аналитика | SQL views (`analytics.*`), Python-сервисы |
| UI | Streamlit (6 разделов на русском) |
| Инфраструктура | Docker Compose (`db`, `api`, `dashboard`) |
| Качество | pytest, GitHub Actions (`.github/workflows/ci.yml`) |

Стек документации: Markdown, Mermaid и PlantUML (диаграммы как код), OpenAPI 3.0.3 (YAML), JSON Schema 2020-12.

## Как читать диаграммы

Диаграммы в `.md` написаны на Mermaid — GitHub показывает их как картинки прямо на странице.
Исходники в PlantUML (BPMN-дорожки, C4 через `!include <C4/...>`) лежат в [diagrams/](diagrams/); под каждой диаграммой есть ссылка на её `.puml`.
Отрисовать PlantUML можно на [plantuml.com](https://www.plantuml.com/plantuml/uml/) или расширением *PlantUML* в VS Code.

OpenAPI-спецификацию удобно смотреть в [Swagger Editor](https://editor.swagger.io/): *File → Import file → `api/openapi.yaml`*.

## Структура раздела

```text
docs/system-analysis/
├── README.md
├── 01-business-context.md
├── 02-requirements.md
├── 03-process-bpmn.md
├── 04-data-model.md
├── 05-api.md
├── 06-sequence.md
├── 07-integration.md
├── 08-nfr-architecture.md
├── 09-glossary.md
├── api/
│   └── openapi.yaml
└── diagrams/          # исходники PlantUML (*.puml)
```
