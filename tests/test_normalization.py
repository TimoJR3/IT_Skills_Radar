from app.services.normalization import clean_text
from app.services.normalization import normalize_employment_type
from app.services.normalization import normalize_record
from app.services.normalization import normalize_role
from app.services.normalization import normalize_seniority
from app.services.normalization import normalize_skills
from app.services.normalization import normalize_work_format


def test_clean_text_removes_html_and_extra_spaces() -> None:
    raw_value = " <p> Python&nbsp;&nbsp;and   SQL </p> "

    assert clean_text(raw_value) == "Python and SQL"


def test_normalize_role_maps_dirty_title_to_product_analyst() -> None:
    role = normalize_role("Product Analyst (AB tests / BI)")

    assert role.code == "product_analyst"
    assert role.name == "Product Analyst"


def test_normalize_seniority_maps_intern_and_junior_tokens() -> None:
    assert normalize_seniority("Intern Data Analyst") == "intern"
    assert normalize_seniority("Junior Data Scientist") == "junior"


def test_normalize_work_format_detects_remote_and_hybrid() -> None:
    assert normalize_work_format("remote", "Data Analyst", None) == "remote"
    assert normalize_work_format(None, "Data Scientist", "Hybrid work with office visits") == "hybrid"


def test_normalize_employment_type_maps_common_variants() -> None:
    assert normalize_employment_type("full time") == "full_time"
    assert normalize_employment_type("internship") == "internship"


def test_normalize_skills_handles_aliases() -> None:
    skill_matches = normalize_skills(
        title="Junior Data Scientist",
        description_text="Need sklearn, experimentation, dashboard work and SQL.",
        raw_skills=["Postgres", "ML", "Python"],
    )

    skill_slugs = {item.definition.slug for item in skill_matches}

    assert "postgresql" in skill_slugs
    assert "scikit-learn" in skill_slugs
    assert "a_b_testing" in skill_slugs
    assert "machine_learning" in skill_slugs
    assert "bi" in skill_slugs
    assert "sql" in skill_slugs


def test_normalize_record_extracts_clean_fields() -> None:
    record = {
        "id": "demo-101",
        "title": "Junior Data Scientist / ML",
        "company": "Signal AI",
        "location": "Moscow, Russia",
        "description": "<div>Python, pandas, sklearn and Postgres SQL.</div>",
        "skills": ["Python", "pandas", "sklearn", "Postgres"],
        "salary_from": "120000",
        "salary_to": "180000",
        "currency": "RUR",
        "gross_type": "gross",
        "salary_period": "month",
        "url": "https://example.local/demo-101",
        "employment_type": "full_time",
        "work_format": "hybrid",
        "published_at": "2026-04-12T10:00:00+03:00",
    }

    normalized = normalize_record(record=record, source_name="manual")

    assert normalized.source_vacancy_id == "demo-101"
    assert normalized.role.code == "data_scientist"
    assert normalized.seniority_level == "junior"
    assert normalized.city == "Moscow"
    assert normalized.country == "Russia"
    assert normalized.salary is not None
    assert normalized.salary.currency_code == "RUB"
    assert normalized.description_text == "Python, pandas, sklearn and Postgres SQL."
