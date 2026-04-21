# Data Dictionary

## Общая идея

Схема разделена на два слоя:
- нормализованный слой для аналитики: `roles`, `skills`, `vacancies`, `vacancy_skills`, `salary_info`
- raw-слой для следа источника: `raw_source_metadata`

Такой дизайн помогает одновременно:
- строить чистые аналитические запросы
- не терять исходный payload вакансии
- позже безопасно развивать ingestion и нормализацию

## Таблицы

### `roles`

Справочник нормализованных ролей.

| Поле | Тип | Описание |
|---|---|---|
| `id` | `bigserial` | PK роли |
| `role_code` | `text` | Стабильный код роли, например `data_scientist` |
| `role_name_ru` | `text` | Человеко-понятное имя роли |
| `role_group` | `text` | Группа роли: `data`, `analytics`, `product`, `ml` |
| `created_at` | `timestamptz` | Время создания записи |

### `skills`

Справочник нормализованных навыков.

| Поле | Тип | Описание |
|---|---|---|
| `id` | `bigserial` | PK навыка |
| `skill_name` | `text` | Каноническое название навыка, например `Python` |
| `skill_slug` | `text` | Нормализованный slug, например `python` |
| `skill_category` | `text` | Категория навыка: `database`, `ml`, `analytics` и т.д. |
| `is_active` | `boolean` | Признак активности навыка |
| `created_at` | `timestamptz` | Время создания записи |

### `vacancies`

Главная сущность проекта: нормализованная вакансия.

| Поле | Тип | Описание |
|---|---|---|
| `id` | `bigserial` | PK вакансии |
| `source_name` | `text` | Источник вакансии: `hh_ru`, `habr_career`, `superjob`, `manual` |
| `source_vacancy_id` | `text` | ID вакансии в источнике |
| `role_id` | `bigint` | FK на `roles.id` |
| `title` | `text` | Заголовок вакансии |
| `company_name` | `text` | Название компании |
| `city` | `text` | Город |
| `country` | `text` | Страна, по умолчанию `Россия` |
| `seniority_level` | `text` | Уровень: `intern`, `junior`, `middle`, `senior`, `lead`, `unknown` |
| `employment_type` | `text` | Тип занятости |
| `work_format` | `text` | Формат работы: `office`, `remote`, `hybrid`, `unknown` |
| `description_text` | `text` | Нормализованный текст описания вакансии |
| `vacancy_url` | `text` | Ссылка на оригинал вакансии |
| `published_at` | `timestamptz` | Когда вакансия была опубликована в источнике |
| `collected_at` | `timestamptz` | Когда вакансия была собрана системой |
| `is_active` | `boolean` | Признак актуальности вакансии |
| `created_at` | `timestamptz` | Техническое время создания |
| `updated_at` | `timestamptz` | Техническое время обновления |

### `salary_info`

Отдельная таблица зарплаты в формате 1:1 с вакансией.

| Поле | Тип | Описание |
|---|---|---|
| `vacancy_id` | `bigint` | PK и FK на `vacancies.id` |
| `salary_from` | `numeric(12,2)` | Нижняя граница зарплаты |
| `salary_to` | `numeric(12,2)` | Верхняя граница зарплаты |
| `currency_code` | `char(3)` | Валюта: `RUB`, `USD`, `EUR` |
| `gross_type` | `text` | Тип зарплаты: `gross`, `net`, `unknown` |
| `salary_period` | `text` | Период: `month`, `year`, `project`, `unknown` |
| `salary_comment` | `text` | Текстовое пояснение |
| `created_at` | `timestamptz` | Время создания записи |

Почему зарплата вынесена отдельно:
- не у всех вакансий есть зарплата
- так проще фильтровать вакансии с зарплатой и без
- это делает модель чище для salary premium аналитики

### `vacancy_skills`

Связующая таблица many-to-many между вакансиями и навыками.

| Поле | Тип | Описание |
|---|---|---|
| `vacancy_id` | `bigint` | FK на `vacancies.id` |
| `skill_id` | `bigint` | FK на `skills.id` |
| `is_required` | `boolean` | Насколько навык обязателен |
| `match_source` | `text` | Откуда найден навык: `description`, `title`, `manual`, `llm`, `regex` |
| `created_at` | `timestamptz` | Время создания записи |

PK составной: `(vacancy_id, skill_id)`.

### `raw_source_metadata`

Хранит raw payload и техническую информацию о сборе.

| Поле | Тип | Описание |
|---|---|---|
| `id` | `bigserial` | PK записи |
| `vacancy_id` | `bigint` | FK на `vacancies.id`, связь 1:1 |
| `source_name` | `text` | Источник вакансии |
| `source_url` | `text` | URL источника |
| `source_payload` | `jsonb` | Исходный JSON/payload вакансии |
| `parser_version` | `text` | Версия парсера |
| `http_status` | `integer` | HTTP status при получении |
| `checksum` | `text` | Хэш полезной нагрузки для дедупликации и отладки |
| `collected_at` | `timestamptz` | Когда payload был собран |
| `created_at` | `timestamptz` | Время создания записи |

## Связи

- `roles 1 -> N vacancies`
- `vacancies 1 -> 0..1 salary_info`
- `vacancies N <-> N skills` через `vacancy_skills`
- `vacancies 1 -> 0..1 raw_source_metadata`

## Почему модель именно такая

Это практичный вариант для portfolio-проекта:
- достаточно нормализованная, чтобы строить аналитику
- достаточно простая, чтобы объяснить за 3-5 минут
- легко расширяется под ingestion, API и dashboard
- raw и curated данные не смешиваются в одной таблице
