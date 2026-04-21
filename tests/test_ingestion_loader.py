import json
from pathlib import Path

from app.services.ingestion import load_source_records
from app.services.ingestion import run_ingestion
from app.services.ingestion import validate_required_fields


def test_load_source_records_from_json(tmp_path: Path) -> None:
    source_path = tmp_path / "vacancies.json"
    source_path.write_text(
        json.dumps(
            [
                {
                    "id": "json-1",
                    "title": "Data Analyst",
                    "company": "Example",
                }
            ]
        ),
        encoding="utf-8",
    )

    records = load_source_records(source_path)

    assert len(records) == 1
    assert records[0]["id"] == "json-1"


def test_load_source_records_from_csv(tmp_path: Path) -> None:
    source_path = tmp_path / "vacancies.csv"
    source_path.write_text(
        "id,title,company\ncsv-1,Product Analyst,Example\n",
        encoding="utf-8",
    )

    records = load_source_records(source_path)

    assert len(records) == 1
    assert records[0]["title"] == "Product Analyst"


def test_validate_required_fields_reports_missing_values() -> None:
    errors = validate_required_fields({"id": "broken-1", "company": "Example"})

    assert "Missing required field: title" in errors


def test_run_ingestion_supports_dry_run(tmp_path: Path) -> None:
    source_path = tmp_path / "vacancies.json"
    source_path.write_text(
        json.dumps(
            [
                {
                    "id": "good-1",
                    "title": "ML Engineer",
                    "company": "Vision Lab",
                    "description": "Machine learning, Python and Git.",
                },
                {
                    "id": "bad-1",
                    "company": "Broken Corp",
                },
            ]
        ),
        encoding="utf-8",
    )

    result = run_ingestion(
        input_path=source_path,
        source_name="manual",
        dry_run=True,
    )

    assert result.total_records == 2
    assert result.valid_records == 1
    assert result.invalid_records == 1
    assert result.loaded_records == 0
    assert any("bad-1" in error for error in result.errors)
