# Data Dictionary

## Design idea

The storage layer is split into two parts:
- curated entities for analytics: `roles`, `skills`, `vacancies`, `vacancy_skills`, `salary_info`
- raw traceability layer: `raw_source_metadata`

This is a practical middle ground for a portfolio project. The analytics layer stays clean enough for SQL queries and API responses, while the raw layer preserves the original payload for debugging and future parsers.

## ER logic in plain words

- One normalized role can map to many vacancies.
- One vacancy can have zero or one salary record.
- One vacancy can contain many skills, and one skill can appear in many vacancies.
- One vacancy can have zero or one raw metadata record with the original payload from the source.

## Tables

### `roles`

Normalized reference table for target job roles.

| Column | Type | Description |
|---|---|---|
| `id` | `bigserial` | Primary key |
| `role_code` | `text` | Stable machine-friendly code such as `data_scientist` |
| `role_name` | `text` | Canonical display name |
| `role_group` | `text` | Broad family: `data`, `analytics`, `product`, `ml` |
| `created_at` | `timestamptz` | Technical creation timestamp |

Why it exists:
- avoids mixing many title variants directly in analytics
- lets you aggregate `Junior Data Scientist`, `ML Scientist`, `Product Analyst` into clearer groups later

### `skills`

Normalized dictionary of skills.

| Column | Type | Description |
|---|---|---|
| `id` | `bigserial` | Primary key |
| `skill_name` | `text` | Canonical skill name such as `Python` |
| `skill_slug` | `text` | Lowercase stable identifier such as `python` |
| `skill_category` | `text` | Optional grouping such as `database`, `ml`, `bi` |
| `is_active` | `boolean` | Whether the skill is active in the dictionary |
| `created_at` | `timestamptz` | Technical creation timestamp |

Why it exists:
- skills need a reusable canonical layer for joins, deduplication and API output
- `skill_slug` is stable even if display text changes

### `vacancies`

Main fact table with one row per normalized vacancy.

| Column | Type | Description |
|---|---|---|
| `id` | `bigserial` | Primary key |
| `source_name` | `text` | Source system such as `hh_ru` |
| `source_vacancy_id` | `text` | Vacancy identifier from the source |
| `role_id` | `bigint` | FK to `roles.id` |
| `title` | `text` | Vacancy title from the source after light normalization |
| `company_name` | `text` | Company name |
| `city` | `text` | City |
| `country` | `text` | Country |
| `seniority_level` | `text` | `intern`, `junior`, `middle`, `senior`, `lead`, `unknown` |
| `employment_type` | `text` | `full_time`, `part_time`, `internship`, `contract`, `project`, `unknown` |
| `work_format` | `text` | `office`, `remote`, `hybrid`, `unknown` |
| `description_text` | `text` | Vacancy description text |
| `vacancy_url` | `text` | Original public URL |
| `published_at` | `timestamptz` | When the vacancy was published at the source |
| `collected_at` | `timestamptz` | When your pipeline collected the vacancy |
| `is_active` | `boolean` | Whether the vacancy is currently active in your store |
| `created_at` | `timestamptz` | Technical creation timestamp |
| `updated_at` | `timestamptz` | Technical update timestamp |

Why it exists:
- this is the central entity for analytics
- it keeps both business attributes and time fields needed for trend analysis
- `published_at` is for market dynamics, `collected_at` is for pipeline lineage

### `salary_info`

Optional 1:1 table for salary data.

| Column | Type | Description |
|---|---|---|
| `vacancy_id` | `bigint` | PK and FK to `vacancies.id` |
| `salary_from` | `numeric(12,2)` | Lower bound |
| `salary_to` | `numeric(12,2)` | Upper bound |
| `salary_mid` | `numeric(12,2)` | Generated midpoint for analytics |
| `currency_code` | `char(3)` | `RUB`, `USD`, `EUR` |
| `gross_type` | `text` | `gross`, `net`, `unknown` |
| `salary_period` | `text` | `month`, `year`, `project`, `unknown` |
| `salary_comment` | `text` | Free-text comment |
| `created_at` | `timestamptz` | Technical creation timestamp |

Why salary is separated:
- many vacancies have no salary
- salary analytics should work only on valid salary rows
- this keeps the vacancy table simpler and avoids sparse columns

### `vacancy_skills`

Bridge table for many-to-many relation between vacancies and skills.

| Column | Type | Description |
|---|---|---|
| `vacancy_id` | `bigint` | FK to `vacancies.id` |
| `skill_id` | `bigint` | FK to `skills.id` |
| `is_required` | `boolean` | Whether the skill looks required rather than optional |
| `match_source` | `text` | How the skill was matched: `title`, `description`, `manual`, `llm`, `regex` |
| `created_at` | `timestamptz` | Technical creation timestamp |

Primary key:
- `(vacancy_id, skill_id)`

Why it exists:
- top skills and salary premium both depend on a clean many-to-many join
- this table is the core bridge for all skill-level analytics

### `raw_source_metadata`

Optional raw payload and parser trace for each vacancy.

| Column | Type | Description |
|---|---|---|
| `id` | `bigserial` | Primary key |
| `vacancy_id` | `bigint` | Unique FK to `vacancies.id` |
| `source_name` | `text` | Source system |
| `source_url` | `text` | Raw source URL |
| `source_payload` | `jsonb` | Original payload or a compact snapshot |
| `parser_version` | `text` | Parser version |
| `http_status` | `integer` | HTTP status from collection |
| `checksum` | `text` | Payload checksum for dedup/debug |
| `collected_at` | `timestamptz` | Collection timestamp from the raw layer |
| `created_at` | `timestamptz` | Technical creation timestamp |

Why it exists:
- lets you debug parsing without cluttering analytics tables
- supports reprocessing and future ingestion work

## Relationships

- `roles 1 -> N vacancies`
- `vacancies 1 -> 0..1 salary_info`
- `vacancies N <-> N skills` through `vacancy_skills`
- `vacancies 1 -> 0..1 raw_source_metadata`

## Constraints and integrity rules

The schema intentionally uses simple but useful constraints:

- `UNIQUE (source_name, source_vacancy_id)` prevents duplicate source records.
- Role codes and skill slugs are unique and machine-friendly.
- Enumerated `CHECK` constraints keep `seniority_level`, `work_format`, `employment_type`, `gross_type` and other controlled values consistent.
- Salary checks enforce non-negative amounts and valid ranges.
- `published_at <= collected_at` prevents impossible time sequences.
- Foreign keys keep roles, skills and salary rows attached to valid vacancies.
- URL checks reject obviously malformed links.

## Indexes and why they matter

### `idx_vacancies_role_seniority_published_at`

Supports filtering by normalized role and seniority with time ordering.

Useful for:
- junior data scientist vacancies
- product analyst trends over time

### `idx_vacancies_published_at`

Supports time-series scans and month-based aggregations.

Useful for:
- skill dynamics by month
- recent vacancies dashboards

### `idx_vacancies_collected_at`

Useful for operational queries around ingestion freshness.

### `idx_vacancies_country_city`

Supports location filters without creating a more complex location model.

### `idx_vacancies_is_active`

Partial index for the common case when only active vacancies matter.

### `idx_salary_info_currency_period_mid`

Helps salary analysis over comparable salaries.

Useful for:
- salary premium by skill within `RUB` and `month`
- filtering rows with actual salary values

### `idx_vacancy_skills_skill_id_vacancy_id`

Essential for skill-centric aggregation.

Useful for:
- top skills
- salary premium by skill

### `idx_vacancy_skills_vacancy_id_required`

Useful when you need to fetch all skills for a vacancy or focus on required skills only.

### `idx_skills_category`

Supports optional grouping by skill category in dashboards.

### `idx_raw_source_metadata_checksum`

Useful for deduplication checks in future ingestion.

### `idx_raw_source_metadata_payload_gin`

Lets you inspect JSON payload fields efficiently if debugging raw data.

## What analytics this schema supports

This model directly supports:

- top skills by role
- top required skills by role
- skill demand dynamics by month using `published_at`
- comparisons between `data scientist`, `data analyst`, `product analyst`
- salary premium by skill using `salary_mid`
- filtering by `intern`, `junior`, `middle`, `senior`
- filtering by city, country, work format and source

## Example query patterns

Top skills by normalized role:

```sql
SELECT
    r.role_name,
    s.skill_name,
    COUNT(*) AS vacancy_count
FROM vacancies v
JOIN roles r ON r.id = v.role_id
JOIN vacancy_skills vs ON vs.vacancy_id = v.id
JOIN skills s ON s.id = vs.skill_id
GROUP BY r.role_name, s.skill_name
ORDER BY r.role_name, vacancy_count DESC;
```

Monthly skill dynamics:

```sql
SELECT
    DATE_TRUNC('month', v.published_at) AS month,
    s.skill_name,
    COUNT(*) AS mentions
FROM vacancies v
JOIN vacancy_skills vs ON vs.vacancy_id = v.id
JOIN skills s ON s.id = vs.skill_id
WHERE v.published_at IS NOT NULL
GROUP BY month, s.skill_name
ORDER BY month, mentions DESC;
```

Salary premium by skill:

```sql
SELECT
    s.skill_name,
    AVG(si.salary_mid) AS avg_salary_mid
FROM salary_info si
JOIN vacancy_skills vs ON vs.vacancy_id = si.vacancy_id
JOIN skills s ON s.id = vs.skill_id
WHERE si.currency_code = 'RUB'
  AND si.salary_period = 'month'
GROUP BY s.skill_name
ORDER BY avg_salary_mid DESC;
```

## How to explain this in an interview

Use a short story:

1. `vacancies` is the main fact table.
2. `roles` and `skills` are normalized dictionaries for stable analytics dimensions.
3. `vacancy_skills` handles the many-to-many relation needed for skill analytics.
4. `salary_info` is split out because salary is optional and should stay analytically clean.
5. `raw_source_metadata` preserves source payloads for debugging and future ingestion work.

The key point is that the model is intentionally simple, but already shaped around real product questions: what skills are demanded, how demand changes over time, and whether some skills are associated with higher salaries.
