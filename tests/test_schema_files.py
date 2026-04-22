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


def test_sample_sources_exist() -> None:
    assert (BASE_DIR / "data" / "samples" / "prepared_vacancies.json").exists()
    assert (BASE_DIR / "data" / "samples" / "prepared_vacancies.csv").exists()
