from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def test_sql_files_exist() -> None:
    assert (BASE_DIR / "sql" / "01_init_schema.sql").exists()
    assert (BASE_DIR / "sql" / "02_seed_data.sql").exists()
    assert (BASE_DIR / "sql" / "03_analytics_views.sql").exists()


def test_data_dictionary_exists() -> None:
    assert (BASE_DIR / "docs" / "data_dictionary.md").exists()


def test_decisions_doc_exists() -> None:
    assert (BASE_DIR / "docs" / "decisions.md").exists()


def test_analytics_doc_exists() -> None:
    assert (BASE_DIR / "docs" / "analytics.md").exists()


def test_portfolio_docs_exist() -> None:
    assert (BASE_DIR / "docs" / "resume_bullets.md").exists()
    assert (BASE_DIR / "docs" / "interview_story.md").exists()
    assert (BASE_DIR / "docs" / "demo_checklist.md").exists()


def test_ci_and_project_files_exist() -> None:
    assert (BASE_DIR / ".github" / "workflows" / "ci.yml").exists()
    assert (BASE_DIR / ".dockerignore").exists()
    assert (BASE_DIR / "pytest.ini").exists()


def test_sample_sources_exist() -> None:
    assert (BASE_DIR / "data" / "samples" / "prepared_vacancies.json").exists()
    assert (BASE_DIR / "data" / "samples" / "prepared_vacancies.csv").exists()
