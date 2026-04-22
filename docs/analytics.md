# Analytics Layer

## Purpose

This layer prepares reusable aggregates for the future API and dashboard.

The goal is to answer a small set of practical questions:
- which skills appear most often
- how skill demand changes over time
- which skills are more typical for specific roles
- which skills are associated with higher salaries
- what junior and intern role snapshots look like

The implementation uses PostgreSQL views in the `analytics` schema and a lightweight Python service that reads from those views.

## Analytics views

### `analytics.top_skills_by_role`

What it shows:
- top skills inside each role and seniority bucket

Main fields:
- `role_code`
- `seniority_level`
- `skill_slug`
- `vacancy_count`
- `vacancy_share`
- `skill_rank`

Formula in plain words:
- `vacancy_count` = how many distinct vacancies of a role mention the skill
- `vacancy_share` = `vacancy_count / total vacancies in the same role and seniority`

How to read it:
- if `vacancy_share = 0.60`, then 60% of vacancies in that slice mention the skill

### `analytics.skills_trend_monthly`

What it shows:
- monthly dynamics of skill mentions

Main fields:
- `month_start`
- `role_code`
- `seniority_level`
- `skill_slug`
- `vacancy_count`
- `vacancy_share`

Formula in plain words:
- month is based on `published_at`, or `collected_at` if `published_at` is missing
- `vacancy_share` = skill mentions in the month divided by total vacancies in the same month, role and seniority

How to read it:
- this helps compare growth or decline in demand over time

### `analytics.role_skill_distribution`

What it shows:
- how a skill is distributed across roles
- how deeply a skill penetrates each role

Main fields:
- `role_code`
- `skill_slug`
- `vacancy_count`
- `skill_penetration_in_role`
- `role_share_of_skill`
- `required_share`

Formulas in plain words:
- `skill_penetration_in_role` = share of vacancies in that role where the skill appears
- `role_share_of_skill` = share of all vacancies with the skill that belongs to the role
- `required_share` = share of matched vacancies where the skill is marked as required

How to read it:
- high `skill_penetration_in_role` means the skill is common inside the role
- high `role_share_of_skill` means the role contributes a large part of that skill's total demand

### `analytics.skill_salary_premium`

What it shows:
- practical salary comparison for vacancies with a skill versus without it

Main fields:
- `role_code`
- `skill_slug`
- `vacancies_with_skill`
- `vacancies_without_skill`
- `median_salary_with_skill`
- `median_salary_without_skill`
- `salary_premium_abs`
- `salary_premium_pct`

Formula in plain words:
- only comparable salaries are used: `RUB`, `month`, and non-null `salary_mid`
- `median_salary_with_skill` = median salary of vacancies with the skill
- `median_salary_without_skill` = median salary of vacancies in the same role without the skill
- `salary_premium_abs` = `with skill median - without skill median`
- `salary_premium_pct` = `(with skill median - without skill median) / without skill median`

Why median:
- it is easier to explain than more advanced models
- it is less sensitive to outliers than average

### `analytics.junior_roles_overview`

What it shows:
- a compact snapshot of `intern` and `junior` vacancy slices

Main fields:
- `role_code`
- `seniority_level`
- `total_vacancies`
- `salary_vacancies`
- `salary_coverage`
- `median_salary_mid`
- `average_salary_mid`

Formula in plain words:
- `salary_coverage` = share of vacancies in the slice with comparable salary data

## Python service

The service lives in `app/services/analytics.py`.

It provides:
- `get_top_skills_by_role()`
- `get_skills_trend_monthly()`
- `get_skill_salary_premium()`
- `get_role_skill_distribution()`
- `get_junior_roles_overview()`

Why this service exists:
- future API endpoints can call it directly
- Streamlit can reuse the same interface
- SQL stays in views, while Python handles filters and output formatting

## Example checks

Top skills for junior data scientist roles:

```sql
SELECT *
FROM analytics.top_skills_by_role
WHERE role_code = 'data_scientist'
  AND seniority_level = 'junior'
  AND skill_rank <= 10
ORDER BY skill_rank;
```

Monthly trend for SQL in junior and intern roles:

```sql
SELECT *
FROM analytics.skills_trend_monthly
WHERE skill_slug = 'sql'
  AND seniority_level IN ('intern', 'junior')
ORDER BY month_start, role_code;
```

Salary premium for Python:

```sql
SELECT *
FROM analytics.skill_salary_premium
WHERE skill_slug = 'python'
ORDER BY salary_premium_abs DESC;
```

## How to validate results

Use simple spot checks:

1. Pick one role and manually count how many vacancies mention SQL.
2. Compare that number to `vacancy_count` in `top_skills_by_role`.
3. Pick one skill and one month and manually count matching vacancies.
4. Compare raw salary rows with medians in `skill_salary_premium`.

This is a good interview habit because it shows you do not treat aggregates as a black box.

## Interpretation limits

These metrics are useful, but they are not causal.

Important limitations:
- a skill may correlate with salary because it appears in stronger roles, not because the skill itself causes higher pay
- small sample sizes can make medians unstable
- missing salary data creates selection bias
- skill extraction is rule-based, so some mentions will be missed or overcounted
- `published_at` may be absent, so some trends fall back to `collected_at`

## Portfolio story

This analytics layer shows a good progression:
- raw vacancy ingestion
- normalized storage model
- reusable analytical views
- lightweight service layer ready for API and dashboard integration

That makes the project feel closer to a small data product rather than a notebook-only exercise.
