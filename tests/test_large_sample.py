from pathlib import Path

from app.services.large_sample import generate_records
from app.services.large_sample import write_records


def test_generate_records_is_deterministic() -> None:
    first = generate_records(count=5, seed=7)
    second = generate_records(count=5, seed=7)

    assert first == second


def test_generate_records_has_required_fields() -> None:
    records = generate_records(count=25, seed=11)

    assert len(records) == 25
    assert len({record["id"] for record in records}) == 25
    assert all(record["title"] for record in records)
    assert all(record["company"] for record in records)
    assert all(record["skills"] for record in records)
    assert {record["currency"] for record in records} == {"RUB"}


def test_write_records_creates_json_file(tmp_path: Path) -> None:
    output_path = tmp_path / "large_sample.json"
    records = generate_records(count=3, seed=3)

    write_records(records, output_path)

    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8").startswith("[")
