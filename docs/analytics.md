# Аналитический слой

## Назначение

Этот слой готовит переиспользуемые агрегаты для API и dashboard.

Он отвечает на ключевые вопросы:
- какие навыки встречаются чаще всего;
- как меняется спрос на навыки по времени;
- какие навыки характерны для разных ролей;
- какие навыки связаны с более высокой зарплатой;
- как выглядит срез junior и intern ролей.

Реализация состоит из PostgreSQL views в схеме `analytics` и легкого Python-сервиса, который читает эти витрины.

## Витрины

### `analytics.top_skills_by_role`

Что показывает:
- топ навыков внутри роли и уровня seniority.

Основные поля:
- `role_code`
- `seniority_level`
- `skill_slug`
- `vacancy_count`
- `vacancy_share`
- `skill_rank`

Формула простыми словами:
- `vacancy_count` = сколько уникальных вакансий роли упоминают навык;
- `vacancy_share` = `vacancy_count / общее число вакансий в той же роли и на том же уровне`.

### `analytics.skills_trend_monthly`

Что показывает:
- динамику навыков по месяцам.

Основные поля:
- `month_start`
- `role_code`
- `seniority_level`
- `skill_slug`
- `vacancy_count`
- `vacancy_share`

Формула:
- месяц берется из `published_at`, а если его нет — из `collected_at`;
- `vacancy_share` = доля вакансий месяца, где встречается навык.

### `analytics.role_skill_distribution`

Что показывает:
- насколько навык характерен для роли;
- какую долю общего спроса на навык дает каждая роль.

Основные поля:
- `role_code`
- `skill_slug`
- `vacancy_count`
- `skill_penetration_in_role`
- `role_share_of_skill`
- `required_share`

Формулы:
- `skill_penetration_in_role` = доля вакансий роли, где встречается навык;
- `role_share_of_skill` = доля всех вакансий с навыком, приходящаяся на роль;
- `required_share` = доля вакансий, где навык отмечен как required.

### `analytics.skill_salary_premium`

Что показывает:
- практическое сравнение зарплаты вакансий с навыком и без навыка.

Основные поля:
- `role_code`
- `skill_slug`
- `vacancies_with_skill`
- `vacancies_without_skill`
- `median_salary_with_skill`
- `median_salary_without_skill`
- `salary_premium_abs`
- `salary_premium_pct`

Формула:
- берутся только сопоставимые зарплаты: `RUB`, `month`, `salary_mid IS NOT NULL`;
- `median_salary_with_skill` = медианная зарплата вакансий с навыком;
- `median_salary_without_skill` = медианная зарплата вакансий той же роли без навыка;
- `salary_premium_abs` = разница медиан;
- `salary_premium_pct` = относительная разница медиан.

Почему используется медиана:
- ее проще объяснить;
- она устойчивее к выбросам, чем среднее.

### `analytics.junior_roles_overview`

Что показывает:
- компактный срез по `intern` и `junior`.

Основные поля:
- `role_code`
- `seniority_level`
- `total_vacancies`
- `salary_vacancies`
- `salary_coverage`
- `median_salary_mid`
- `average_salary_mid`

Формула:
- `salary_coverage` = доля вакансий в срезе, где есть сопоставимая зарплата.

## Python-сервис

Сервис находится в `app/services/analytics.py`.

Он предоставляет:
- `get_top_skills_by_role()`
- `get_skills_trend_monthly()`
- `get_skill_salary_premium()`
- `get_role_skill_distribution()`
- `get_junior_roles_overview()`

Зачем нужен:
- будущие API endpoints работают через него;
- dashboard использует тот же интерфейс;
- SQL остается во views, а Python занимается фильтрацией и форматированием результата.

## Как проверять корректность

Лучший способ — делать spot checks:

1. Выбрать одну роль и вручную посчитать, сколько вакансий содержат `SQL`.
2. Сравнить это число с `vacancy_count` в `top_skills_by_role`.
3. Выбрать навык и месяц и вручную сверить `skills_trend_monthly`.
4. Сравнить исходные зарплаты с медианами в `skill_salary_premium`.

Такой подход хорошо смотрится на собеседовании, потому что показывает, что ты не воспринимаешь агрегаты как черный ящик.

## Ограничения интерпретации

Эти метрики полезны, но они не доказывают причинно-следственную связь.

Важно помнить:
- навык может коррелировать с зарплатой просто потому, что встречается в более сильных ролях;
- маленькая выборка делает медианы нестабильными;
- неполные зарплатные данные вносят selection bias;
- extraction навыков rule-based и может недоучитывать или переучитывать часть упоминаний;
- если `published_at` отсутствует, временная динамика опирается на `collected_at`.

## Портфельная история

Этот слой делает проект похожим не на набор ноутбуков, а на маленький data product:
- есть ingestion;
- есть нормализованное хранилище;
- есть аналитические витрины;
- есть сервисный слой для API;
- есть UI поверх готовых агрегатов.
