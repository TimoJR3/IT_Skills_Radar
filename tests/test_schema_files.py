from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


def test_sql_files_exist() -> None:
    assert (BASE_DIR / "sql" / "01_init_schema.sql").exists()
    assert (BASE_DIR / "sql" / "02_seed_data.sql").exists()


def test_data_dictionary_exists() -> None:
    assert (BASE_DIR / "docs" / "data_dictionary.md").exists()
