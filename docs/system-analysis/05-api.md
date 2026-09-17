# 05. API

Полная спецификация: [../api/openapi.yaml](api/openapi.yaml) (OpenAPI 3.0.3). Её можно открыть в [Swagger Editor](https://editor.swagger.io/). На запущенном стенде FastAPI сам показывает документацию по адресу `http://localhost:8000/docs`.

Источники фактов: `app/api/routes.py`, `app/schemas/analytics.py`, `app/schemas/health.py`, `app/main.py`.

## 1. Общие принципы

| Принцип | Сейчас | Цель |
|---|---|---|
| Стиль | REST, только `GET`, JSON | То же |
| Базовый URL | `http://localhost:8000` | `/api/v1/...` (проектное решение, в текущей реализации отсутствует) |
| Аутентификация | Нет (локальный демо-стенд) | API-ключ в заголовке `X-API-Key` для внешних потребителей (проектное решение, в текущей реализации отсутствует) |
| Источник данных | Витрины `analytics.*` через `AnalyticsService` | То же |
| Множественные значения | Повтор параметра: `?seniority_levels=intern&seniority_levels=junior` | То же |
| Формат ошибок | `{"detail": ...}` (FastAPI) | `application/problem+json`, RFC 9457 (проектное решение, в текущей реализации отсутствует) |
| Пагинация | Нет; объём ограничен `rank_limit` (1–30) для топа | `limit`/`offset` для трендов при росте данных (проектное решение, в текущей реализации отсутствует) |

## 2. Эндпоинты

| Метод и путь | Назначение | Параметры | Витрина | Требование | Статус |
|---|---|---|---|---|---|
| `GET /health` | Проверка доступности | — | — | US-08 | Реализовано |
| `GET /roles` | Список ролей для фильтров | — | справочник ролей | UC-01 | Реализовано |
| `GET /skills/top` | Топ навыков по роли и грейду | `role_code`, `seniority_levels[]`, `rank_limit` (1–30, по умолчанию 10) | `analytics.top_skills_by_role` | US-01 | Реализовано |
| `GET /skills/trends` | Помесячная динамика | `skill_slug`, `role_code`, `seniority_levels[]` | `analytics.skills_trend_monthly` | US-02 | Реализовано |
| `GET /salary/premium` | Зарплатный сигнал навыка | `skill_slug`, `role_code`, `seniority_levels[]` | `analytics.skill_salary_premium` | US-04 | Реализовано |
| `GET /overview/junior` | Срез junior/intern | — | `analytics.junior_roles_overview` | US-05 | Реализовано |
| `GET /skills/distribution` | Распределение навыков по ролям | `skill_slug`, `role_code`, `seniority_levels[]` | `analytics.role_skill_distribution` | US-03 | Проектное решение, в текущей реализации отсутствует (витрина и схема ответа в коде есть) |
| `GET /ingestion/runs/{run_id}` | Сводка прогона загрузки | `run_id` (uuid) | `ingestion_runs` | US-07 | Проектное решение, в текущей реализации отсутствует |

Все параметры фильтров необязательны: если параметр не передан, фильтр не применяется.

## 3. Коды ответов

| Код | Когда | Тело сейчас | Статус |
|---|---|---|---|
| 200 | Успех, в том числе пустой список | JSON-массив | Реализовано |
| 400 | Семантически неверный фильтр (например, `seniority_levels=trainee`) | `problem+json` | Проектное решение, в текущей реализации отсутствует: сейчас вернётся `200 []` |
| 404 | Неизвестный `role_code`; прогон `run_id` не найден | `problem+json` | Проектное решение, в текущей реализации отсутствует: сейчас неизвестная роль даёт `200 []` |
| 422 | Нарушен тип или диапазон параметра (`rank_limit=0`, `rank_limit=abc`) | `{"detail": [{"loc", "msg", "type"}]}` | Реализовано (FastAPI) |
| 500 | Непредвиденная ошибка | `{"detail": "Не удалось получить данные для операции '…'."}` | Реализовано |
| 503 | БД недоступна, не инициализирована или витрины не созданы | `{"detail": "База данных не инициализирована, недоступна или аналитические витрины еще не созданы для операции '…'."}` | Реализовано |

Разделение 400 и 422 в целевом контракте: **422** — параметр не прошёл синтаксическую проверку (тип, диапазон); **400** — параметр синтаксически верен, но недопустим по смыслу (значение вне справочника).

## 4. Примеры

### 4.1. Проверка доступности

```http
GET /health HTTP/1.1
Host: localhost:8000
```

```json
{ "status": "ok" }
```

### 4.2. Топ навыков для junior Data Analyst

```bash
curl "http://localhost:8000/skills/top?role_code=data_analyst&seniority_levels=junior&rank_limit=3"
```

Ответ `200 OK` (значения условные):

```json
[
  {
    "role_code": "data_analyst",
    "role_name": "Data Analyst",
    "seniority_level": "junior",
    "skill_slug": "sql",
    "skill_name": "SQL",
    "vacancy_count": 42,
    "vacancy_share": 0.84,
    "skill_rank": 1
  },
  {
    "role_code": "data_analyst",
    "role_name": "Data Analyst",
    "seniority_level": "junior",
    "skill_slug": "python",
    "skill_name": "Python",
    "vacancy_count": 31,
    "vacancy_share": 0.62,
    "skill_rank": 2
  },
  {
    "role_code": "data_analyst",
    "role_name": "Data Analyst",
    "seniority_level": "junior",
    "skill_slug": "bi",
    "skill_name": "BI / Visualization",
    "vacancy_count": 25,
    "vacancy_share": 0.5,
    "skill_rank": 3
  }
]
```

### 4.3. Динамика Python для intern и junior

```bash
curl "http://localhost:8000/skills/trends?skill_slug=python&seniority_levels=intern&seniority_levels=junior"
```

```json
[
  {
    "month_start": "2026-04-01",
    "role_code": "data_scientist",
    "role_name": "Data Scientist",
    "seniority_level": "junior",
    "skill_slug": "python",
    "skill_name": "Python",
    "vacancy_count": 12,
    "vacancy_share": 0.92
  }
]
```

### 4.4. Зарплатный сигнал

```bash
curl "http://localhost:8000/salary/premium?skill_slug=python&role_code=data_analyst"
```

```json
[
  {
    "role_code": "data_analyst",
    "role_name": "Data Analyst",
    "seniority_level": "junior",
    "skill_slug": "python",
    "skill_name": "Python",
    "vacancies_with_skill": 20,
    "vacancies_without_skill": 14,
    "median_salary_with_skill": 110000.0,
    "median_salary_without_skill": 95000.0,
    "salary_premium_abs": 15000.0,
    "salary_premium_pct": 0.1579
  }
]
```

Дашборд обязан показывать рядом дисклеймер: сигнал корреляционный, учитываются только зарплаты в RUB за месяц.

### 4.5. Ошибка валидации — текущий формат (реализовано)

```bash
curl -i "http://localhost:8000/skills/top?rank_limit=31"
```

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/json
```

```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["query", "rank_limit"],
      "msg": "Input should be less than or equal to 30",
      "input": "31",
      "ctx": { "le": 30 }
    }
  ]
}
```

Точный текст `msg` зависит от версии Pydantic.

### 4.6. Ошибка валидации — целевой формат problem+json (проектное решение, в текущей реализации отсутствует)

```http
HTTP/1.1 422 Unprocessable Entity
Content-Type: application/problem+json
```

```json
{
  "type": "https://it-skills-radar.local/problems/validation-error",
  "title": "Ошибка валидации параметров",
  "status": 422,
  "detail": "rank_limit должен быть от 1 до 30",
  "instance": "/skills/top",
  "request_id": "8c1e4b7c",
  "errors": [
    { "parameter": "rank_limit", "message": "Значение 31 больше максимума 30" }
  ]
}
```

### 4.7. Неизвестная роль (проектное решение, в текущей реализации отсутствует)

```http
GET /skills/top?role_code=qa_engineer HTTP/1.1

HTTP/1.1 404 Not Found
Content-Type: application/problem+json
```

```json
{
  "type": "https://it-skills-radar.local/problems/role-not-found",
  "title": "Роль не найдена",
  "status": 404,
  "detail": "Роль с кодом qa_engineer отсутствует в справочнике",
  "instance": "/skills/top",
  "request_id": "8c1e4b7b"
}
```

### 4.8. БД недоступна (реализовано)

```http
HTTP/1.1 503 Service Unavailable
Content-Type: application/json
```

```json
{
  "detail": "База данных не инициализирована, недоступна или аналитические витрины еще не созданы для операции 'топ навыков'."
}
```

## 5. Правила развития контракта

Весь раздел — проектное решение, в текущей реализации отсутствует.

- Добавление необязательного параметра или поля ответа — не ломающее изменение, версия `MINOR`.
- Удаление или переименование поля, изменение типа, новый обязательный параметр — ломающее изменение, только в `/api/v2`.
- Старая версия поддерживается не менее 3 месяцев после выхода новой; об устаревании сообщает заголовок `Deprecation`.
- Каждое изменение контракта сопровождается обновлением `openapi.yaml` и контрактным тестом (сейчас есть `tests/test_api.py`).
