# 06. Sequence-диаграммы

| ID | Сценарий | Статус | Связи |
|---|---|---|---|
| SD-01 | Загрузка вакансий из файла через CLI | Реализовано | US-06, US-07, BPMN AS-IS |
| SD-02 | Запрос дашборда «Карта рынка» через API | Реализовано | US-01, UC-01, `GET /skills/top` |
| SD-03 | Обработка ошибок валидации: запись файла и параметр API | Реализовано; ветка журнала и problem+json — проектное решение | US-07, US-01 AC3 |

Имена функций и классов взяты из `app/services/ingestion.py`, `app/api/routes.py`, `dashboard/api_client.py`.

## SD-01. Загрузка вакансий из файла (реализовано)

```plantuml
@startuml
title SD-01. Загрузка вакансий из JSON/CSV
autonumber
actor "Владелец данных" as D
participant "CLI\napp.services.ingestion" as CLI
participant "normalization.py" as N
participant "PostgresIngestionWriter" as W
database "PostgreSQL" as DB

D -> CLI : python -m app.services.ingestion\n--input data/samples/prepared_vacancies.json --source manual
activate CLI
CLI -> CLI : load_source_records()\nJSON: массив или {"items": [...]}; CSV: DictReader
loop для каждой записи
  CLI -> CLI : validate_required_fields()\nsource_vacancy_id, title, company_name
  alt обязательного поля нет
    CLI -> CLI : invalid_records += 1\nerrors += "Missing required field: ..."
  else запись валидна
    CLI -> N : clean_text(), роль, грейд,\nнавыки, зарплата, формат работы
    N --> CLI : нормализованная вакансия
  end
end
alt режим --dry-run
  CLI --> D : IngestionResult (loaded_records = 0)
else обычный режим
  CLI -> W : write(нормализованные вакансии)
  activate W
  loop для каждой вакансии
    W -> DB : _upsert_role()\nON CONFLICT (role_code)
    DB --> W : role_id
    W -> DB : _upsert_vacancy()\nON CONFLICT (source_name, source_vacancy_id)
    DB --> W : vacancy_id
    alt зарплата указана
      W -> DB : _upsert_salary()\nON CONFLICT (vacancy_id)
    else зарплаты нет
      W -> DB : удалить строку salary_info
    end
    W -> DB : _replace_skills()\nудалить связи, _upsert_skill(), вставить vacancy_skills
    W -> DB : _upsert_raw_metadata()\nsource_payload, checksum sha256,\nparser_version = rule_based_v1
  end
  W --> CLI : loaded_records
  deactivate W
  CLI --> D : JSON-сводка: total_records, valid_records,\ninvalid_records, loaded_records, errors
end
deactivate CLI
@enduml
```

Ключевые решения:

- Повторный запуск безопасен: все записи — upsert по бизнес-ключам.
- Связи навыков пересобираются целиком, поэтому удалённый из вакансии навык не «зависает» в `vacancy_skills`.
- Витрины — обычные `VIEW`, данные в них актуальны сразу после записи.

## SD-02. Запрос дашборда через API (реализовано)

```plantuml
@startuml
title SD-02. Раздел «Карта рынка»: топ навыков
autonumber
actor "Пользователь" as U
participant "Streamlit\ndashboard/app.py" as S
participant "ApiClient\n(timeout 20 с)" as C
participant "FastAPI\nroutes.py" as A
participant "AnalyticsService" as AS
database "PostgreSQL\nanalytics.*" as DB

U -> S : открыть «Карта рынка»
S -> C : get roles
C -> A : GET /roles
A -> AS : get_roles()
AS -> DB : SELECT роли
DB --> AS : строки
AS --> A : list[dict]
A --> C : 200 [RoleItem]
C --> S : ApiResult(ok = true)
S --> U : фильтры роли и грейда

U -> S : роль = data_analyst, грейд = junior
S -> C : get top skills
C -> A : GET /skills/top?role_code=data_analyst\n&seniority_levels=junior&rank_limit=10
activate A
A -> A : валидация Query-параметров\n(rank_limit 1..30)
A -> AS : get_top_skills_by_role(role_code,\nseniority_levels, rank_limit)
AS -> DB : SELECT ... FROM analytics.top_skills_by_role\nWHERE ... AND skill_rank <= :rank_limit
alt данные получены
  DB --> AS : 0..N строк
  AS --> A : list[dict]
  A --> C : 200 [TopSkillItem]
  C --> S : ApiResult(ok = true, data)
  alt список пуст
    S --> U : «Нет данных для выбранных фильтров»
  else есть строки
    S --> U : график и таблица навыков
  end
else SQLAlchemyError (БД недоступна / витрины не созданы)
  DB --> AS : ошибка
  AS --> A : исключение
  A --> C : 503 {"detail": "База данных не инициализирована..."}
  C --> S : ApiResult(ok = false, status_code = 503)
  S --> U : сообщение об ошибке
end
deactivate A

note over C : При httpx.RequestError (нет соединения, таймаут)\nApiClient возвращает ApiResult(ok = false)\nбез повторов. Повтор — действие пользователя.
@enduml
```

Условие `skill_rank <= :rank_limit` показывает смысл фильтра; точный текст SQL-запроса находится в `app/services/analytics.py`.

## SD-03. Обработка ошибок валидации

Две ветки: ошибка данных при загрузке и ошибка параметра при запросе к API. Шаги, помеченные `[проект]`, — (проектное решение, в текущей реализации отсутствует).

```plantuml
@startuml
title SD-03. Ошибки валидации: загрузка и API
autonumber

actor "Владелец данных" as D
participant "CLI ingestion" as CLI
database "PostgreSQL" as DB
actor "Пользователь" as U
participant "Streamlit" as S
participant "FastAPI" as A

== Ветка 1. Запись файла без обязательного поля ==
D -> CLI : --input vacancies.json (3 записи)
activate CLI
CLI -> CLI : validate_required_fields(запись 2)
note right of CLI : нет company_name
CLI -> CLI : пропустить запись,\ninvalid_records = 1
CLI -> DB : upsert записей 1 и 3
DB --> CLI : OK
opt [проект] журнал загрузок
  CLI -> DB : INSERT ingestion_runs\n(status = partial, errors)
end
CLI --> D : {"total_records": 3, "valid_records": 2,\n"invalid_records": 1, "loaded_records": 2,\n"errors": ["Missing required field: company_name"]}
deactivate CLI
D -> D : исправить источник и\nповторить загрузку (upsert, без дублей)

== Ветка 2. Некорректный параметр запроса ==
U -> S : ввести количество навыков = 31
S -> A : GET /skills/top?rank_limit=31
activate A
A -> A : проверка Query(ge = 1, le = 30)
alt текущая реализация
  A --> S : 422 application/json\n{"detail": [{"loc": ["query","rank_limit"], ...}]}
else [проект] problem+json
  A --> S : 422 application/problem+json\n{"type", "title", "status": 422, "errors": [...], "request_id"}
end
deactivate A
note right of A : Запрос в БД не выполняется
S --> U : «Некорректный фильтр»,\nзначение сброшено к 10

== Ветка 3. [проект] Значение вне справочника ==
U -> S : роль = qa_engineer (из закладки)
S -> A : GET /skills/top?role_code=qa_engineer
activate A
A -> DB : проверить role_code в roles
DB --> A : не найдено
A --> S : 404 application/problem+json\n"Роль не найдена"
deactivate A
S --> U : «Роль не найдена», фильтр сброшен
note over A : Сейчас неизвестная роль даёт 200 и пустой список
@enduml
```
