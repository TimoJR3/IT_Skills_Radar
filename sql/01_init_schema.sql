CREATE TABLE IF NOT EXISTS roles (
    id BIGSERIAL PRIMARY KEY,
    role_code TEXT NOT NULL UNIQUE,
    role_name TEXT NOT NULL UNIQUE,
    role_group TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_roles_role_code_format
        CHECK (role_code ~ '^[a-z0-9_]+$'),
    CONSTRAINT chk_roles_role_group
        CHECK (role_group IN ('data', 'analytics', 'product', 'ml'))
);


CREATE TABLE IF NOT EXISTS skills (
    id BIGSERIAL PRIMARY KEY,
    skill_name TEXT NOT NULL,
    skill_slug TEXT NOT NULL UNIQUE,
    skill_category TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_skills_slug_format
        CHECK (skill_slug = LOWER(skill_slug)),
    CONSTRAINT chk_skills_category_not_blank
        CHECK (skill_category IS NULL OR LENGTH(TRIM(skill_category)) > 0)
);


CREATE TABLE IF NOT EXISTS vacancies (
    id BIGSERIAL PRIMARY KEY,
    source_name TEXT NOT NULL,
    source_vacancy_id TEXT NOT NULL,
    role_id BIGINT NOT NULL REFERENCES roles (id) ON DELETE RESTRICT,
    title TEXT NOT NULL,
    company_name TEXT NOT NULL,
    city TEXT,
    country TEXT NOT NULL DEFAULT 'Russia',
    seniority_level TEXT NOT NULL DEFAULT 'unknown',
    employment_type TEXT NOT NULL DEFAULT 'unknown',
    work_format TEXT NOT NULL DEFAULT 'unknown',
    description_text TEXT,
    vacancy_url TEXT,
    published_at TIMESTAMPTZ,
    collected_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_vacancies_source_item UNIQUE (source_name, source_vacancy_id),
    CONSTRAINT chk_vacancies_source_name
        CHECK (source_name IN ('hh_ru', 'habr_career', 'superjob', 'manual')),
    CONSTRAINT chk_vacancies_seniority_level
        CHECK (seniority_level IN ('intern', 'junior', 'middle', 'senior', 'lead', 'unknown')),
    CONSTRAINT chk_vacancies_employment_type
        CHECK (employment_type IN ('full_time', 'part_time', 'internship', 'contract', 'project', 'unknown')),
    CONSTRAINT chk_vacancies_work_format
        CHECK (work_format IN ('office', 'remote', 'hybrid', 'unknown')),
    CONSTRAINT chk_vacancies_country_not_blank
        CHECK (LENGTH(TRIM(country)) > 0),
    CONSTRAINT chk_vacancies_dates
        CHECK (published_at IS NULL OR published_at <= collected_at),
    CONSTRAINT chk_vacancies_url_format
        CHECK (
            vacancy_url IS NULL
            OR vacancy_url ~ '^https?://'
        )
);


CREATE TABLE IF NOT EXISTS salary_info (
    vacancy_id BIGINT PRIMARY KEY REFERENCES vacancies (id) ON DELETE CASCADE,
    salary_from NUMERIC(12, 2),
    salary_to NUMERIC(12, 2),
    salary_mid NUMERIC(12, 2) GENERATED ALWAYS AS (
        CASE
            WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL
                THEN ROUND((salary_from + salary_to) / 2.0, 2)
            ELSE COALESCE(salary_from, salary_to)
        END
    ) STORED,
    currency_code CHAR(3) NOT NULL DEFAULT 'RUB',
    gross_type TEXT NOT NULL DEFAULT 'unknown',
    salary_period TEXT NOT NULL DEFAULT 'month',
    salary_comment TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_salary_bounds_positive
        CHECK (
            (salary_from IS NULL OR salary_from >= 0)
            AND (salary_to IS NULL OR salary_to >= 0)
        ),
    CONSTRAINT chk_salary_bounds_order
        CHECK (salary_from IS NULL OR salary_to IS NULL OR salary_from <= salary_to),
    CONSTRAINT chk_salary_has_any_value
        CHECK (salary_from IS NOT NULL OR salary_to IS NOT NULL),
    CONSTRAINT chk_salary_currency
        CHECK (currency_code IN ('RUB', 'USD', 'EUR')),
    CONSTRAINT chk_salary_gross_type
        CHECK (gross_type IN ('gross', 'net', 'unknown')),
    CONSTRAINT chk_salary_period
        CHECK (salary_period IN ('month', 'year', 'project', 'unknown'))
);


CREATE TABLE IF NOT EXISTS vacancy_skills (
    vacancy_id BIGINT NOT NULL REFERENCES vacancies (id) ON DELETE CASCADE,
    skill_id BIGINT NOT NULL REFERENCES skills (id) ON DELETE RESTRICT,
    is_required BOOLEAN NOT NULL DEFAULT TRUE,
    match_source TEXT NOT NULL DEFAULT 'description',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (vacancy_id, skill_id),
    CONSTRAINT chk_vacancy_skills_match_source
        CHECK (match_source IN ('title', 'description', 'manual', 'llm', 'regex'))
);


CREATE TABLE IF NOT EXISTS raw_source_metadata (
    id BIGSERIAL PRIMARY KEY,
    vacancy_id BIGINT NOT NULL UNIQUE REFERENCES vacancies (id) ON DELETE CASCADE,
    source_name TEXT NOT NULL,
    source_url TEXT,
    source_payload JSONB NOT NULL,
    parser_version TEXT NOT NULL DEFAULT 'v1',
    http_status INTEGER,
    checksum TEXT,
    collected_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_raw_metadata_source_name
        CHECK (source_name IN ('hh_ru', 'habr_career', 'superjob', 'manual')),
    CONSTRAINT chk_raw_metadata_http_status
        CHECK (http_status IS NULL OR http_status BETWEEN 100 AND 599),
    CONSTRAINT chk_raw_metadata_url_format
        CHECK (
            source_url IS NULL
            OR source_url ~ '^https?://'
        )
);


CREATE INDEX IF NOT EXISTS idx_vacancies_role_seniority_published_at
    ON vacancies (role_id, seniority_level, published_at DESC);

CREATE INDEX IF NOT EXISTS idx_vacancies_published_at
    ON vacancies (published_at DESC);

CREATE INDEX IF NOT EXISTS idx_vacancies_collected_at
    ON vacancies (collected_at DESC);

CREATE INDEX IF NOT EXISTS idx_vacancies_country_city
    ON vacancies (country, city);

CREATE INDEX IF NOT EXISTS idx_vacancies_is_active
    ON vacancies (is_active)
    WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_salary_info_currency_period_mid
    ON salary_info (currency_code, salary_period, salary_mid)
    WHERE salary_mid IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_vacancy_skills_skill_id_vacancy_id
    ON vacancy_skills (skill_id, vacancy_id);

CREATE INDEX IF NOT EXISTS idx_vacancy_skills_vacancy_id_required
    ON vacancy_skills (vacancy_id, is_required);

CREATE INDEX IF NOT EXISTS idx_skills_category
    ON skills (skill_category);

CREATE INDEX IF NOT EXISTS idx_raw_source_metadata_checksum
    ON raw_source_metadata (checksum);

CREATE INDEX IF NOT EXISTS idx_raw_source_metadata_payload_gin
    ON raw_source_metadata
    USING GIN (source_payload);
