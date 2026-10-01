# 06. Sequence-диаграммы

| ID | Сценарий | Статус | Связи |
|---|---|---|---|
| SD-01 | Загрузка вакансий из файла через CLI | Реализовано | US-06, US-07, BPMN AS-IS |
| SD-02 | Запрос дашборда «Карта рынка» через API | Реализовано | US-01, UC-01, `GET /skills/top` |
| SD-03 | Обработка ошибок валидации: запись файла и параметр API | Реализовано; ветка журнала и problem+json — проектное решение | US-07, US-01 AC3 |

Имена функций и классов взяты из `app/services/ingestion.py`, `app/api/routes.py`, `dashboard/api_client.py`.

## SD-01. Загрузка вакансий из файла (реализовано)

```mermaid
sequenceDiagram
    autonumber
    actor D as Владелец данных
    participant CLI as CLI app.services.ingestion
    participant N as normalization.py
    participant W as PostgresIngestionWriter
    participant DB as PostgreSQL

    D->>+CLI: python -m app.services.ingestion<br/>--input data/samples/prepared_vacancies.json --source manual
    CLI->>CLI: load_source_records()<br/>JSON: массив или {"items": [...]}, CSV: DictReader
    loop для каждой записи
        CLI->>CLI: validate_required_fields()<br/>source_vacancy_id, title, company_name
        alt обязательного поля нет
            CLI->>CLI: invalid_records += 1<br/>errors += "Missing required field: ..."
        else запись валидна
            CLI->>N: clean_text(), роль, грейд,<br/>навыки, зарплата, формат работы
            N-->>CLI: нормализованная вакансия
        end
    end
    alt режим --dry-run
        CLI-->>D: IngestionResult (loaded_records = 0)
    else обычный режим
        CLI->>+W: write(нормализованные вакансии)
        loop для каждой вакансии
            W->>DB: _upsert_role()<br/>ON CONFLICT (role_code)
            DB-->>W: role_id
            W->>DB: _upsert_vacancy()<br/>ON CONFLICT (source_name, source_vacancy_id)
            DB-->>W: vacancy_id
            alt зарплата указана
                W->>DB: _upsert_salary()<br/>ON CONFLICT (vacancy_id)
            else зарплаты нет
                W->>DB: удалить строку salary_info
            end
            W->>DB: _replace_skills()<br/>удалить связи, _upsert_skill(), вставить vacancy_skills
            W->>DB: _upsert_raw_metadata()<br/>source_payload, checksum sha256,<br/>parser_version = rule_based_v1
        end
        W-->>-CLI: loaded_records
        CLI-->>D: JSON-сводка: total_records, valid_records,<br/>invalid_records, loaded_records, errors
    end
    deactivate CLI
```

Исходник PlantUML: [diagrams/sd-01-ingestion.puml](diagrams/sd-01-ingestion.puml)

Ключевые решения:

- Повторный запуск безопасен: все записи — upsert по бизнес-ключам.
- Связи навыков пересобираются целиком, поэтому удалённый из вакансии навык не «зависает» в `vacancy_skills`.
- Витрины — обычные `VIEW`, данные в них актуальны сразу после записи.

## SD-02. Запрос дашборда через API (реализовано)

```mermaid
sequenceDiagram
    autonumber
    actor U as Пользователь
    participant S as Streamlit dashboard/app.py
    participant C as ApiClient (timeout 20 с)
    participant A as FastAPI routes.py
    participant AS as AnalyticsService
    participant DB as PostgreSQL analytics.*

    U->>S: открыть «Карта рынка»
    S->>C: get roles
    C->>A: GET /roles
    A->>AS: get_roles()
    AS->>DB: SELECT роли
    DB-->>AS: строки
    AS-->>A: list[dict]
    A-->>C: 200 [RoleItem]
    C-->>S: ApiResult(ok = true)
    S-->>U: фильтры роли и грейда

    U->>S: роль = data_analyst, грейд = junior
    S->>C: get top skills
    C->>+A: GET /skills/top?role_code=data_analyst<br/>&seniority_levels=junior&rank_limit=10
    A->>A: валидация Query-параметров<br/>(rank_limit 1..30)
    A->>AS: get_top_skills_by_role(role_code,<br/>seniority_levels, rank_limit)
    AS->>DB: SELECT ... FROM analytics.top_skills_by_role<br/>WHERE ... AND skill_rank <= :rank_limit
    alt данные получены
        DB-->>AS: 0..N строк
        AS-->>A: list[dict]
        A-->>C: 200 [TopSkillItem]
        C-->>S: ApiResult(ok = true, data)
        alt список пуст
            S-->>U: «Нет данных для выбранных фильтров»
        else есть строки
            S-->>U: график и таблица навыков
        end
    else SQLAlchemyError (БД недоступна / витрины не созданы)
        DB-->>AS: ошибка
        AS-->>A: исключение
        A-->>C: 503 {"detail": "База данных не инициализирована..."}
        C-->>S: ApiResult(ok = false, status_code = 503)
        S-->>U: сообщение об ошибке
    end
    deactivate A

    Note over C: При httpx.RequestError (нет соединения, таймаут)<br/>ApiClient возвращает ApiResult(ok = false)<br/>без повторов. Повтор — действие пользователя.
```

Исходник PlantUML: [diagrams/sd-02-top-skills.puml](diagrams/sd-02-top-skills.puml)

Условие `skill_rank <= :rank_limit` показывает смысл фильтра; точный текст SQL-запроса находится в `app/services/analytics.py`.

## SD-03. Обработка ошибок валидации

Две ветки: ошибка данных при загрузке и ошибка параметра при запросе к API. Шаги, помеченные `[проект]`, — (проектное решение, в текущей реализации отсутствует).

```mermaid
sequenceDiagram
    autonumber
    actor D as Владелец данных
    participant CLI as CLI ingestion
    participant DB as PostgreSQL
    actor U as Пользователь
    participant S as Streamlit
    participant A as FastAPI

    rect rgba(128, 128, 128, 0.08)
    Note over D,DB: Ветка 1. Запись файла без обязательного поля
    D->>+CLI: --input vacancies.json (3 записи)
    CLI->>CLI: validate_required_fields(запись 2)
    Note right of CLI: нет company_name
    CLI->>CLI: пропустить запись,<br/>invalid_records = 1
    CLI->>DB: upsert записей 1 и 3
    DB-->>CLI: OK
    opt [проект] журнал загрузок
        CLI->>DB: INSERT ingestion_runs<br/>(status = partial, errors)
    end
    CLI-->>-D: {"total_records": 3, "valid_records": 2,<br/>"invalid_records": 1, "loaded_records": 2,<br/>"errors": ["Missing required field: company_name"]}
    D->>D: исправить источник и<br/>повторить загрузку (upsert, без дублей)
    end

    rect rgba(128, 128, 128, 0.08)
    Note over U,A: Ветка 2. Некорректный параметр запроса
    U->>S: ввести количество навыков = 31
    S->>+A: GET /skills/top?rank_limit=31
    A->>A: проверка Query(ge = 1, le = 30)
    alt текущая реализация
        A-->>S: 422 application/json<br/>{"detail": [{"loc": ["query","rank_limit"], ...}]}
    else [проект] problem+json
        A-->>S: 422 application/problem+json<br/>{"type", "title", "status": 422, "errors": [...], "request_id"}
    end
    deactivate A
    Note right of A: Запрос в БД не выполняется
    S-->>U: «Некорректный фильтр»,<br/>значение сброшено к 10
    end

    rect rgba(128, 128, 128, 0.08)
    Note over U,A: Ветка 3. [проект] Значение вне справочника
    U->>S: роль = qa_engineer (из закладки)
    S->>+A: GET /skills/top?role_code=qa_engineer
    A->>DB: проверить role_code в roles
    DB-->>A: не найдено
    A-->>-S: 404 application/problem+json<br/>"Роль не найдена"
    S-->>U: «Роль не найдена», фильтр сброшен
    Note over A: Сейчас неизвестная роль даёт 200 и пустой список
    end
```

Исходник PlantUML: [diagrams/sd-03-validation-errors.puml](diagrams/sd-03-validation-errors.puml)
