INSERT INTO roles (role_code, role_name, role_group)
VALUES
    ('data_scientist', 'Data Scientist', 'data'),
    ('product_analyst', 'Product Analyst', 'product'),
    ('data_analyst', 'Data Analyst', 'analytics'),
    ('intern_analyst', 'Intern Analyst', 'analytics')
ON CONFLICT (role_code) DO NOTHING;


INSERT INTO skills (skill_name, skill_slug, skill_category)
VALUES
    ('Python', 'python', 'programming'),
    ('SQL', 'sql', 'database'),
    ('pandas', 'pandas', 'analytics'),
    ('NumPy', 'numpy', 'analytics'),
    ('scikit-learn', 'scikit-learn', 'ml'),
    ('A/B testing', 'a_b_testing', 'product_analytics'),
    ('PostgreSQL', 'postgresql', 'database'),
    ('Git', 'git', 'tooling'),
    ('Tableau', 'tableau', 'bi')
ON CONFLICT (skill_slug) DO NOTHING;


INSERT INTO vacancies (
    source_name,
    source_vacancy_id,
    role_id,
    title,
    company_name,
    city,
    country,
    seniority_level,
    employment_type,
    work_format,
    description_text,
    vacancy_url,
    published_at,
    collected_at
)
VALUES
    (
        'hh_ru',
        'hh-1001',
        (SELECT id FROM roles WHERE role_code = 'data_scientist'),
        'Junior Data Scientist',
        'TechLab',
        'Moscow',
        'Russia',
        'junior',
        'full_time',
        'hybrid',
        'Python, pandas, SQL and scikit-learn for model development and data preparation.',
        'https://hh.ru/vacancy/1001',
        '2026-04-01 09:00:00+03',
        '2026-04-02 10:15:00+03'
    ),
    (
        'hh_ru',
        'hh-1002',
        (SELECT id FROM roles WHERE role_code = 'product_analyst'),
        'Product Analyst',
        'MarketPlatform',
        'Saint Petersburg',
        'Russia',
        'middle',
        'full_time',
        'remote',
        'Strong SQL, A/B testing and PostgreSQL for product analytics and experiment analysis.',
        'https://hh.ru/vacancy/1002',
        '2026-04-03 11:30:00+03',
        '2026-04-03 12:00:00+03'
    ),
    (
        'habr_career',
        'hc-2001',
        (SELECT id FROM roles WHERE role_code = 'data_analyst'),
        'Junior Data Analyst',
        'FinTech Service',
        'Kazan',
        'Russia',
        'junior',
        'full_time',
        'office',
        'SQL, Python, pandas, Tableau and data quality checks.',
        'https://career.habr.com/vacancies/2001',
        '2026-04-05 14:00:00+03',
        '2026-04-05 14:05:00+03'
    ),
    (
        'manual',
        'demo-3001',
        (SELECT id FROM roles WHERE role_code = 'intern_analyst'),
        'Intern Data Analyst',
        'Demo Analytics',
        'Moscow',
        'Russia',
        'intern',
        'internship',
        'hybrid',
        'Internship with SQL, basic Python and support in EDA tasks.',
        'https://example.local/vacancies/3001',
        '2026-04-06 10:00:00+03',
        '2026-04-06 10:10:00+03'
    )
ON CONFLICT (source_name, source_vacancy_id) DO NOTHING;


INSERT INTO salary_info (
    vacancy_id,
    salary_from,
    salary_to,
    currency_code,
    gross_type,
    salary_period,
    salary_comment
)
VALUES
    (
        (SELECT id FROM vacancies WHERE source_name = 'hh_ru' AND source_vacancy_id = 'hh-1001'),
        120000,
        180000,
        'RUB',
        'gross',
        'month',
        'Range depends on interview results'
    ),
    (
        (SELECT id FROM vacancies WHERE source_name = 'hh_ru' AND source_vacancy_id = 'hh-1002'),
        180000,
        260000,
        'RUB',
        'net',
        'month',
        'Fixed compensation plus bonus'
    ),
    (
        (SELECT id FROM vacancies WHERE source_name = 'habr_career' AND source_vacancy_id = 'hc-2001'),
        90000,
        130000,
        'RUB',
        'gross',
        'month',
        NULL
    )
ON CONFLICT (vacancy_id) DO NOTHING;


INSERT INTO vacancy_skills (vacancy_id, skill_id, is_required, match_source)
VALUES
    (
        (SELECT id FROM vacancies WHERE source_name = 'hh_ru' AND source_vacancy_id = 'hh-1001'),
        (SELECT id FROM skills WHERE skill_slug = 'python'),
        TRUE,
        'description'
    ),
    (
        (SELECT id FROM vacancies WHERE source_name = 'hh_ru' AND source_vacancy_id = 'hh-1001'),
        (SELECT id FROM skills WHERE skill_slug = 'pandas'),
        TRUE,
        'description'
    ),
    (
        (SELECT id FROM vacancies WHERE source_name = 'hh_ru' AND source_vacancy_id = 'hh-1001'),
        (SELECT id FROM skills WHERE skill_slug = 'sql'),
        TRUE,
        'description'
    ),
    (
        (SELECT id FROM vacancies WHERE source_name = 'hh_ru' AND source_vacancy_id = 'hh-1001'),
        (SELECT id FROM skills WHERE skill_slug = 'scikit-learn'),
        TRUE,
        'description'
    ),
    (
        (SELECT id FROM vacancies WHERE source_name = 'hh_ru' AND source_vacancy_id = 'hh-1002'),
        (SELECT id FROM skills WHERE skill_slug = 'sql'),
        TRUE,
        'description'
    ),
    (
        (SELECT id FROM vacancies WHERE source_name = 'hh_ru' AND source_vacancy_id = 'hh-1002'),
        (SELECT id FROM skills WHERE skill_slug = 'a_b_testing'),
        TRUE,
        'description'
    ),
    (
        (SELECT id FROM vacancies WHERE source_name = 'hh_ru' AND source_vacancy_id = 'hh-1002'),
        (SELECT id FROM skills WHERE skill_slug = 'postgresql'),
        FALSE,
        'description'
    ),
    (
        (SELECT id FROM vacancies WHERE source_name = 'habr_career' AND source_vacancy_id = 'hc-2001'),
        (SELECT id FROM skills WHERE skill_slug = 'sql'),
        TRUE,
        'description'
    ),
    (
        (SELECT id FROM vacancies WHERE source_name = 'habr_career' AND source_vacancy_id = 'hc-2001'),
        (SELECT id FROM skills WHERE skill_slug = 'python'),
        FALSE,
        'description'
    ),
    (
        (SELECT id FROM vacancies WHERE source_name = 'habr_career' AND source_vacancy_id = 'hc-2001'),
        (SELECT id FROM skills WHERE skill_slug = 'pandas'),
        TRUE,
        'description'
    ),
    (
        (SELECT id FROM vacancies WHERE source_name = 'habr_career' AND source_vacancy_id = 'hc-2001'),
        (SELECT id FROM skills WHERE skill_slug = 'tableau'),
        FALSE,
        'description'
    ),
    (
        (SELECT id FROM vacancies WHERE source_name = 'manual' AND source_vacancy_id = 'demo-3001'),
        (SELECT id FROM skills WHERE skill_slug = 'sql'),
        TRUE,
        'manual'
    ),
    (
        (SELECT id FROM vacancies WHERE source_name = 'manual' AND source_vacancy_id = 'demo-3001'),
        (SELECT id FROM skills WHERE skill_slug = 'python'),
        FALSE,
        'manual'
    )
ON CONFLICT (vacancy_id, skill_id) DO NOTHING;


INSERT INTO raw_source_metadata (
    vacancy_id,
    source_name,
    source_url,
    source_payload,
    parser_version,
    http_status,
    checksum,
    collected_at
)
VALUES
    (
        (SELECT id FROM vacancies WHERE source_name = 'hh_ru' AND source_vacancy_id = 'hh-1001'),
        'hh_ru',
        'https://hh.ru/vacancy/1001',
        '{"title": "Junior Data Scientist", "area": "Moscow", "salary": {"from": 120000, "to": 180000, "currency": "RUR"}}'::jsonb,
        'v1',
        200,
        'hh1001checksum',
        '2026-04-02 10:15:00+03'
    ),
    (
        (SELECT id FROM vacancies WHERE source_name = 'hh_ru' AND source_vacancy_id = 'hh-1002'),
        'hh_ru',
        'https://hh.ru/vacancy/1002',
        '{"title": "Product Analyst", "area": "Saint Petersburg", "salary": {"from": 180000, "to": 260000, "currency": "RUR"}}'::jsonb,
        'v1',
        200,
        'hh1002checksum',
        '2026-04-03 12:00:00+03'
    ),
    (
        (SELECT id FROM vacancies WHERE source_name = 'habr_career' AND source_vacancy_id = 'hc-2001'),
        'habr_career',
        'https://career.habr.com/vacancies/2001',
        '{"title": "Junior Data Analyst", "city": "Kazan", "salary": {"from": 90000, "to": 130000, "currency": "RUB"}}'::jsonb,
        'v1',
        200,
        'hc2001checksum',
        '2026-04-05 14:05:00+03'
    )
ON CONFLICT (vacancy_id) DO NOTHING;
