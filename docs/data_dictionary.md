# Словарь данных

## Общая идея

Схема разделена на два слоя:
- нормализованный аналитический слой: `roles`, `skills`, `vacancies`, `vacancy_skills`, `salary_info`;
- raw-слой для трассировки источника: `raw_source_metadata`.

Такой дизайн помогает одновременно:
- строить понятные аналитические запросы;
- не терять исходный payload вакансии;
- безопасно развивать ingestion и правила нормализации.

## ER-логика простыми словами

- одна нормализованная роль связана со многими вакансиями;
- одна вакансия может иметь ноль или одну запись о зарплате;
- одна вакансия может содержать много навыков, и один навык может встречаться во многих вакансиях;
- одна вакансия может иметь ноль или одну запись с raw metadata.

## Таблицы

### `roles`

Справочник нормализованных ролей.

| Поле | Тип | Описание |
|---|---|---|
| `id` | `bigserial` | Первичный ключ |
| `role_code` | `text` | Стабильный машинный код, например `data_scientist` |
| `role_name` | `text` | Каноническое отображаемое имя |
| `role_group` | `text` | Группа роли: `data`, `analytics`, `product`, `ml` |
| `created_at` | `timestamptz` | Время создания записи |

Зачем нужна:
- чтобы не строить аналитику по грязным заголовкам вакансий;
- чтобы агрегировать похожие названия в одну роль.

### `skills`

Справочник нормализованных навыков.

| Поле | Тип | Описание |
|---|---|---|
| `id` | `bigserial` | Первичный ключ |
| `skill_name` | `text` | Каноническое имя навыка, например `Python` |
| `skill_slug` | `text` | Стабильный slug, например `python` |
| `skill_category` | `text` | Категория навыка |
| `is_active` | `boolean` | Активен ли навык в словаре |
| `created_at` | `timestamptz` | Время создания записи |

Зачем нужна:
- чтобы переиспользовать навык в разных вакансиях;
- чтобы удобно делать join и агрегаты.

### `vacancies`

Главная факт-таблица проекта: одна строка соответствует одной нормализованной вакансии.

| Поле | Тип | Описание |
|---|---|---|
| `id` | `bigserial` | Первичный ключ |
| `source_name` | `text` | Источник вакансии |
| `source_vacancy_id` | `text` | ID вакансии в источнике |
| `role_id` | `bigint` | FK на `roles.id` |
| `title` | `text` | Заголовок вакансии |
| `company_name` | `text` | Название компании |
| `city` | `text` | Город |
| `country` | `text` | Страна |
| `seniority_level` | `text` | `intern`, `junior`, `middle`, `senior`, `lead`, `unknown` |
| `employment_type` | `text` | Тип занятости |
| `work_format` | `text` | Формат работы |
| `description_text` | `text` | Описание вакансии |
| `vacancy_url` | `text` | Ссылка на оригинал |
| `published_at` | `timestamptz` | Когда вакансия опубликована |
| `collected_at` | `timestamptz` | Когда вакансия собрана системой |
| `is_active` | `boolean` | Активна ли вакансия |
| `created_at` | `timestamptz` | Время создания записи |
| `updated_at` | `timestamptz` | Время обновления записи |

Зачем нужна:
- это центральная сущность для аналитики;
- в ней хранятся и бизнес-поля, и временные признаки.

### `salary_info`

Отдельная таблица зарплат в формате 1:1 с вакансией.

| Поле | Тип | Описание |
|---|---|---|
| `vacancy_id` | `bigint` | PK и FK на `vacancies.id` |
| `salary_from` | `numeric(12,2)` | Нижняя граница зарплаты |
| `salary_to` | `numeric(12,2)` | Верхняя граница зарплаты |
| `salary_mid` | `numeric(12,2)` | Автоматически рассчитанная середина диапазона |
| `currency_code` | `char(3)` | Валюта |
| `gross_type` | `text` | `gross`, `net`, `unknown` |
| `salary_period` | `text` | `month`, `year`, `project`, `unknown` |
| `salary_comment` | `text` | Текстовый комментарий |
| `created_at` | `timestamptz` | Время создания записи |

Почему вынесена отдельно:
- зарплата есть не у всех вакансий;
- так проще считать salary premium и фильтровать только сопоставимые записи.

### `vacancy_skills`

Связующая таблица many-to-many между вакансиями и навыками.

| Поле | Тип | Описание |
|---|---|---|
| `vacancy_id` | `bigint` | FK на `vacancies.id` |
| `skill_id` | `bigint` | FK на `skills.id` |
| `is_required` | `boolean` | Насколько навык обязателен |
| `match_source` | `text` | Откуда найден навык |
| `created_at` | `timestamptz` | Время создания записи |

Первичный ключ:
- `(vacancy_id, skill_id)`

Зачем нужна:
- это центральный мост для skill analytics;
- без нее нельзя нормально считать топ навыков и salary premium.

### `raw_source_metadata`

Таблица для raw payload и технической информации о сборе.

| Поле | Тип | Описание |
|---|---|---|
| `id` | `bigserial` | Первичный ключ |
| `vacancy_id` | `bigint` | Уникальный FK на `vacancies.id` |
| `source_name` | `text` | Источник данных |
| `source_url` | `text` | URL источника |
| `source_payload` | `jsonb` | Исходный JSON или снимок payload |
| `parser_version` | `text` | Версия парсера |
| `http_status` | `integer` | HTTP status при сборе |
| `checksum` | `text` | Хэш payload |
| `collected_at` | `timestamptz` | Время сбора |
| `created_at` | `timestamptz` | Время создания записи |

Зачем нужна:
- помогает отлаживать ingestion;
- сохраняет исходные данные отдельно от cleaned/final слоя.

## Связи

- `roles 1 -> N vacancies`
- `vacancies 1 -> 0..1 salary_info`
- `vacancies N <-> N skills` через `vacancy_skills`
- `vacancies 1 -> 0..1 raw_source_metadata`

## Ограничения целостности

Схема использует простые, но полезные ограничения:

- `UNIQUE (source_name, source_vacancy_id)` защищает от дублей из одного источника;
- `CHECK`-ограничения фиксируют допустимые значения для `seniority_level`, `work_format`, `employment_type`, `gross_type` и других справочных полей;
- проверки зарплаты запрещают отрицательные значения и некорректные диапазоны;
- `published_at <= collected_at` защищает от невозможной временной последовательности;
- внешние ключи обеспечивают корректные связи между ролями, навыками, вакансиями и зарплатами.

## Индексы и зачем они нужны

### `idx_vacancies_role_seniority_published_at`

Полезен для фильтрации по роли, уровню и времени.

### `idx_vacancies_published_at`

Полезен для time-series запросов и помесячных агрегатов.

### `idx_vacancies_collected_at`

Полезен для технической проверки свежести ingestion.

### `idx_vacancies_country_city`

Полезен для фильтров по локации.

### `idx_vacancies_is_active`

Partial index для частого случая, когда нужны только активные вакансии.

### `idx_salary_info_currency_period_mid`

Нужен для salary analytics по сопоставимым зарплатам.

### `idx_vacancy_skills_skill_id_vacancy_id`

Главный индекс для skill-centric агрегатов.

### `idx_vacancy_skills_vacancy_id_required`

Полезен, когда нужно быстро получить навыки вакансии или долю required навыков.

### `idx_skills_category`

Позволяет быстро группировать навыки по категориям.

### `idx_raw_source_metadata_checksum`

Полезен для дедупликации и технической отладки.

### `idx_raw_source_metadata_payload_gin`

Позволяет искать по полям внутри JSON payload.

## Какие аналитические задачи поддерживает схема

Эта модель уже хорошо подходит для:
- топа навыков по роли;
- динамики навыков по месяцам;
- сравнения ролей между собой;
- salary premium по навыкам;
- фильтрации по `intern`, `junior`, `middle`, `senior`;
- фильтрации по локации, источнику и формату работы.

## Как объяснить на собеседовании

Короткая версия:

1. `vacancies` — это главная факт-таблица.
2. `roles` и `skills` — нормализованные справочники.
3. `vacancy_skills` связывает вакансии и навыки.
4. `salary_info` отделена, потому что зарплата опциональна.
5. `raw_source_metadata` сохраняет исходный payload и не смешивает raw со cleaned/final слоем.

Главная мысль: модель достаточно простая, чтобы ее быстро объяснить, и достаточно практичная, чтобы строить на ней ingestion, API и dashboard.
