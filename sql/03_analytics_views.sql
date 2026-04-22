CREATE SCHEMA IF NOT EXISTS analytics;


CREATE OR REPLACE VIEW analytics.top_skills_by_role AS
WITH role_totals AS (
    SELECT
        v.role_id,
        v.seniority_level,
        COUNT(DISTINCT v.id) AS total_vacancies
    FROM vacancies v
    WHERE v.is_active
    GROUP BY v.role_id, v.seniority_level
),
aggregated AS (
    SELECT
        r.role_code,
        r.role_name,
        v.seniority_level,
        s.skill_slug,
        s.skill_name,
        COUNT(DISTINCT v.id) AS vacancy_count,
        ROUND(
            COUNT(DISTINCT v.id)::NUMERIC / NULLIF(rt.total_vacancies, 0),
            4
        ) AS vacancy_share
    FROM vacancies v
    JOIN roles r
        ON r.id = v.role_id
    JOIN vacancy_skills vs
        ON vs.vacancy_id = v.id
    JOIN skills s
        ON s.id = vs.skill_id
    JOIN role_totals rt
        ON rt.role_id = v.role_id
        AND rt.seniority_level = v.seniority_level
    WHERE v.is_active
    GROUP BY
        r.role_code,
        r.role_name,
        v.seniority_level,
        s.skill_slug,
        s.skill_name,
        rt.total_vacancies
)
SELECT
    role_code,
    role_name,
    seniority_level,
    skill_slug,
    skill_name,
    vacancy_count,
    vacancy_share,
    ROW_NUMBER() OVER (
        PARTITION BY role_code, seniority_level
        ORDER BY vacancy_count DESC, skill_name
    ) AS skill_rank
FROM aggregated;


CREATE OR REPLACE VIEW analytics.skills_trend_monthly AS
WITH monthly_totals AS (
    SELECT
        DATE_TRUNC('month', COALESCE(v.published_at, v.collected_at))::DATE AS month_start,
        v.role_id,
        v.seniority_level,
        COUNT(DISTINCT v.id) AS total_vacancies
    FROM vacancies v
    WHERE v.is_active
    GROUP BY
        DATE_TRUNC('month', COALESCE(v.published_at, v.collected_at))::DATE,
        v.role_id,
        v.seniority_level
)
SELECT
    DATE_TRUNC('month', COALESCE(v.published_at, v.collected_at))::DATE AS month_start,
    r.role_code,
    r.role_name,
    v.seniority_level,
    s.skill_slug,
    s.skill_name,
    COUNT(DISTINCT v.id) AS vacancy_count,
    ROUND(
        COUNT(DISTINCT v.id)::NUMERIC / NULLIF(mt.total_vacancies, 0),
        4
    ) AS vacancy_share
FROM vacancies v
JOIN roles r
    ON r.id = v.role_id
JOIN vacancy_skills vs
    ON vs.vacancy_id = v.id
JOIN skills s
    ON s.id = vs.skill_id
JOIN monthly_totals mt
    ON mt.month_start = DATE_TRUNC('month', COALESCE(v.published_at, v.collected_at))::DATE
    AND mt.role_id = v.role_id
    AND mt.seniority_level = v.seniority_level
WHERE v.is_active
GROUP BY
    DATE_TRUNC('month', COALESCE(v.published_at, v.collected_at))::DATE,
    r.role_code,
    r.role_name,
    v.seniority_level,
    s.skill_slug,
    s.skill_name,
    mt.total_vacancies;


CREATE OR REPLACE VIEW analytics.role_skill_distribution AS
WITH role_totals AS (
    SELECT
        v.role_id,
        v.seniority_level,
        COUNT(DISTINCT v.id) AS total_role_vacancies
    FROM vacancies v
    WHERE v.is_active
    GROUP BY v.role_id, v.seniority_level
),
skill_totals AS (
    SELECT
        s.id AS skill_id,
        v.seniority_level,
        COUNT(DISTINCT v.id) AS total_skill_vacancies
    FROM vacancies v
    JOIN vacancy_skills vs
        ON vs.vacancy_id = v.id
    JOIN skills s
        ON s.id = vs.skill_id
    WHERE v.is_active
    GROUP BY s.id, v.seniority_level
)
SELECT
    r.role_code,
    r.role_name,
    v.seniority_level,
    s.skill_slug,
    s.skill_name,
    COUNT(DISTINCT v.id) AS vacancy_count,
    ROUND(
        COUNT(DISTINCT v.id)::NUMERIC / NULLIF(rt.total_role_vacancies, 0),
        4
    ) AS skill_penetration_in_role,
    ROUND(
        COUNT(DISTINCT v.id)::NUMERIC / NULLIF(st.total_skill_vacancies, 0),
        4
    ) AS role_share_of_skill,
    ROUND(
        COUNT(DISTINCT CASE WHEN vs.is_required THEN v.id END)::NUMERIC
        / NULLIF(COUNT(DISTINCT v.id), 0),
        4
    ) AS required_share
FROM vacancies v
JOIN roles r
    ON r.id = v.role_id
JOIN vacancy_skills vs
    ON vs.vacancy_id = v.id
JOIN skills s
    ON s.id = vs.skill_id
JOIN role_totals rt
    ON rt.role_id = v.role_id
    AND rt.seniority_level = v.seniority_level
JOIN skill_totals st
    ON st.skill_id = s.id
    AND st.seniority_level = v.seniority_level
WHERE v.is_active
GROUP BY
    r.role_code,
    r.role_name,
    v.seniority_level,
    s.skill_slug,
    s.skill_name,
    rt.total_role_vacancies,
    st.total_skill_vacancies;


CREATE OR REPLACE VIEW analytics.junior_roles_overview AS
SELECT
    r.role_code,
    r.role_name,
    v.seniority_level,
    COUNT(DISTINCT v.id) AS total_vacancies,
    COUNT(DISTINCT CASE
        WHEN si.salary_mid IS NOT NULL
            AND si.currency_code = 'RUB'
            AND si.salary_period = 'month'
        THEN v.id
    END) AS salary_vacancies,
    ROUND(
        COUNT(DISTINCT CASE
            WHEN si.salary_mid IS NOT NULL
                AND si.currency_code = 'RUB'
                AND si.salary_period = 'month'
            THEN v.id
        END)::NUMERIC / NULLIF(COUNT(DISTINCT v.id), 0),
        4
    ) AS salary_coverage,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY si.salary_mid)
        FILTER (
            WHERE si.salary_mid IS NOT NULL
              AND si.currency_code = 'RUB'
              AND si.salary_period = 'month'
        ) AS median_salary_mid,
    ROUND(
        AVG(si.salary_mid)
            FILTER (
                WHERE si.salary_mid IS NOT NULL
                  AND si.currency_code = 'RUB'
                  AND si.salary_period = 'month'
            ),
        2
    ) AS average_salary_mid
FROM vacancies v
JOIN roles r
    ON r.id = v.role_id
LEFT JOIN salary_info si
    ON si.vacancy_id = v.id
WHERE v.is_active
  AND v.seniority_level IN ('intern', 'junior')
GROUP BY
    r.role_code,
    r.role_name,
    v.seniority_level;


CREATE OR REPLACE VIEW analytics.skill_salary_premium AS
WITH comparable_salaries AS (
    SELECT
        v.id AS vacancy_id,
        r.role_code,
        r.role_name,
        v.seniority_level,
        si.salary_mid
    FROM vacancies v
    JOIN roles r
        ON r.id = v.role_id
    JOIN salary_info si
        ON si.vacancy_id = v.id
    WHERE v.is_active
      AND si.salary_mid IS NOT NULL
      AND si.currency_code = 'RUB'
      AND si.salary_period = 'month'
),
role_skill_universe AS (
    SELECT DISTINCT
        cs.role_code,
        cs.role_name,
        cs.seniority_level,
        s.skill_slug,
        s.skill_name
    FROM comparable_salaries cs
    JOIN vacancy_skills vs
        ON vs.vacancy_id = cs.vacancy_id
    JOIN skills s
        ON s.id = vs.skill_id
),
flagged AS (
    SELECT
        rsu.role_code,
        rsu.role_name,
        rsu.seniority_level,
        rsu.skill_slug,
        rsu.skill_name,
        cs.vacancy_id,
        cs.salary_mid,
        EXISTS (
            SELECT 1
            FROM vacancy_skills vs
            JOIN skills s
                ON s.id = vs.skill_id
            WHERE vs.vacancy_id = cs.vacancy_id
              AND s.skill_slug = rsu.skill_slug
        ) AS has_skill
    FROM comparable_salaries cs
    JOIN role_skill_universe rsu
        ON rsu.role_code = cs.role_code
        AND rsu.seniority_level = cs.seniority_level
),
aggregated AS (
    SELECT
        role_code,
        role_name,
        seniority_level,
        skill_slug,
        skill_name,
        COUNT(*) FILTER (WHERE has_skill) AS vacancies_with_skill,
        COUNT(*) FILTER (WHERE NOT has_skill) AS vacancies_without_skill,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary_mid)
            FILTER (WHERE has_skill) AS median_salary_with_skill,
        PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary_mid)
            FILTER (WHERE NOT has_skill) AS median_salary_without_skill
    FROM flagged
    GROUP BY
        role_code,
        role_name,
        seniority_level,
        skill_slug,
        skill_name
)
SELECT
    role_code,
    role_name,
    seniority_level,
    skill_slug,
    skill_name,
    vacancies_with_skill,
    vacancies_without_skill,
    median_salary_with_skill,
    median_salary_without_skill,
    ROUND(
    (median_salary_with_skill - median_salary_without_skill)::numeric,
    2
    ) AS salary_premium_abs,
    ROUND(
    (
        (median_salary_with_skill - median_salary_without_skill)
        / NULLIF(median_salary_without_skill, 0)
    )::numeric,
    4
) AS salary_premium_pct
FROM aggregated
WHERE vacancies_with_skill > 0
  AND vacancies_without_skill > 0;
