# Ingestion Decisions

## Goal

This stage adds a simple ingestion pipeline that is easy to explain in a portfolio interview:
- read prepared vacancy data from local JSON or CSV
- validate required fields
- clean messy text
- normalize roles and skills with rule-based logic
- save raw payloads and cleaned final entities into PostgreSQL

## Layer boundaries

### Raw layer

The raw layer is `raw_source_metadata`.

What goes there:
- original source payload from JSON or CSV
- checksum of the payload
- parser version
- collection timestamp

Why it exists:
- keeps traceability
- helps debugging
- lets you improve normalization later without losing the original input

### Cleaned layer

The cleaned layer is created in Python during ingestion before writing to the database.

What happens there:
- required field validation
- whitespace cleanup
- HTML tag removal
- date parsing
- salary parsing
- normalization of role, seniority, work format and skills

Why it is not stored as a separate table yet:
- for this portfolio version it is enough to keep the transformation logic in code
- the final normalized tables already represent the cleaned business-ready layer

### Final layer

The final layer is stored in:
- `vacancies`
- `roles`
- `skills`
- `vacancy_skills`
- `salary_info`

This is the layer used later for analytics and API responses.

## Validation rules

Required fields for the first version:
- `source_vacancy_id`
- `title`
- `company_name`

If one of these fields is missing, the row is skipped and reported in the ingestion summary.

Why only these fields:
- they are enough to identify and store a vacancy
- the first version should stay simple and not reject too much useful data

## Text cleaning rules

Text cleaning is intentionally lightweight:
- HTML tags are removed
- HTML entities are unescaped
- repeated spaces are collapsed
- empty strings become `None`

This handles the most common noise without building a heavy NLP layer.

## Role normalization rules

Role normalization is rule-based and title-driven.

Current canonical roles:
- `data_scientist`
- `data_analyst`
- `product_analyst`
- `ml_engineer`
- `other_data_role`

Examples:
- `Junior Data Scientist / ML` -> role `data_scientist`, seniority `junior`
- `Product Analyst (AB tests / BI)` -> role `product_analyst`
- `ML Engineer` -> role `ml_engineer`
- unknown but adjacent data titles -> `other_data_role`

Why this approach:
- it is understandable
- it is deterministic
- it is easy to extend with a few more rules later

## Skill normalization rules

Skill normalization is also rule-based and combines:
- structured skills field if present
- vacancy title
- vacancy description

Current canonical examples:
- `PostgreSQL`, `Postgres` -> `postgresql`
- `SQL` -> `sql`
- `scikit-learn`, `sklearn` -> `scikit-learn`
- `A/B testing`, `AB test`, `experimentation` -> `a_b_testing`
- `machine learning`, `ML` -> `machine_learning`
- `visualization`, `dashboard`, `Power BI`, `Tableau`, `BI` -> `bi`

Design choice:
- generic `SQL` stays separate from `PostgreSQL`
- structured skill fields are marked as more trusted than regex matches from descriptions

## Salary rules

Salary is optional.

Rules:
- if both bounds are missing, no row is created in `salary_info`
- if at least one bound exists, salary is stored
- `RUR` is normalized to `RUB`
- salary period defaults to `month`

## Upsert strategy

The pipeline uses upserts for:
- roles
- skills
- vacancies
- salary rows
- raw metadata

Why:
- repeated runs should be idempotent
- the same prepared source can be reloaded after normalization changes

For `vacancy_skills`, the current set is replaced on each run for the vacancy.

## Why this version is practical

This is not a production ingestion system yet, but it shows the right engineering habits:
- separate raw and normalized storage concerns
- deterministic normalization
- clear validation rules
- idempotent writes
- tests around the most failure-prone logic

## Known limitations

- no external API connectors yet
- no fuzzy matching for complex role titles
- no multilingual stemming or heavy NLP
- no audit table for rejected rows
- cleaned intermediate layer lives in Python, not as a dedicated database table

These limitations are acceptable for the first ingestion version and leave clear next steps for future iterations.
