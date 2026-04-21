from __future__ import annotations

import argparse
import csv
import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from app.services.normalization import FIELD_ALIASES
from app.services.normalization import NormalizedVacancy
from app.services.normalization import get_field_value
from app.services.normalization import normalize_record

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine


SOURCE_NAMES = {"hh_ru", "habr_career", "superjob", "manual"}


@dataclass(frozen=True)
class IngestionResult:
    total_records: int
    valid_records: int
    invalid_records: int
    loaded_records: int
    errors: list[str]


def load_source_records(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()

    if suffix == ".json":
        payload = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, list):
            return [dict(item) for item in payload]
        if isinstance(payload, dict) and isinstance(payload.get("items"), list):
            return [dict(item) for item in payload["items"]]
        raise ValueError("JSON source must contain a list of records or an 'items' list.")

    if suffix == ".csv":
        with path.open("r", encoding="utf-8", newline="") as file:
            return [dict(row) for row in csv.DictReader(file)]

    raise ValueError(f"Unsupported file format: {path.suffix}")


def validate_required_fields(record: dict[str, Any]) -> list[str]:
    required_fields = {
        "source_vacancy_id": FIELD_ALIASES["source_vacancy_id"],
        "title": FIELD_ALIASES["title"],
        "company_name": FIELD_ALIASES["company_name"],
    }

    errors: list[str] = []
    for field_name in required_fields:
        if get_field_value(record, field_name) is None:
            errors.append(f"Missing required field: {field_name}")
    return errors


def get_default_engine() -> Any:
    try:
        from app.db.session import engine
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Database dependencies are not installed. Run pip install -r requirements.txt first."
        ) from exc

    return engine


class PostgresIngestionWriter:
    def __init__(self, db_engine: Any) -> None:
        self.engine = db_engine

    def write(self, vacancies: list[NormalizedVacancy]) -> int:
        loaded_count = 0
        with self.engine.begin() as connection:
            for vacancy in vacancies:
                role_id = self._upsert_role(connection, vacancy)
                vacancy_id = self._upsert_vacancy(connection, vacancy, role_id)
                self._upsert_salary(connection, vacancy_id, vacancy)
                self._replace_skills(connection, vacancy_id, vacancy)
                self._upsert_raw_metadata(connection, vacancy_id, vacancy)
                loaded_count += 1
        return loaded_count

    @staticmethod
    def _upsert_role(connection: Any, vacancy: NormalizedVacancy) -> int:
        from sqlalchemy import text

        query = text(
            """
            INSERT INTO roles (role_code, role_name, role_group)
            VALUES (:role_code, :role_name, :role_group)
            ON CONFLICT (role_code) DO UPDATE
            SET role_name = EXCLUDED.role_name,
                role_group = EXCLUDED.role_group
            RETURNING id
            """
        )
        result = connection.execute(
            query,
            {
                "role_code": vacancy.role.code,
                "role_name": vacancy.role.name,
                "role_group": vacancy.role.group,
            },
        )
        return int(result.scalar_one())

    @staticmethod
    def _upsert_vacancy(connection: Any, vacancy: NormalizedVacancy, role_id: int) -> int:
        from sqlalchemy import text

        query = text(
            """
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
                collected_at,
                is_active,
                updated_at
            )
            VALUES (
                :source_name,
                :source_vacancy_id,
                :role_id,
                :title,
                :company_name,
                :city,
                :country,
                :seniority_level,
                :employment_type,
                :work_format,
                :description_text,
                :vacancy_url,
                :published_at,
                :collected_at,
                TRUE,
                NOW()
            )
            ON CONFLICT (source_name, source_vacancy_id) DO UPDATE
            SET role_id = EXCLUDED.role_id,
                title = EXCLUDED.title,
                company_name = EXCLUDED.company_name,
                city = EXCLUDED.city,
                country = EXCLUDED.country,
                seniority_level = EXCLUDED.seniority_level,
                employment_type = EXCLUDED.employment_type,
                work_format = EXCLUDED.work_format,
                description_text = EXCLUDED.description_text,
                vacancy_url = EXCLUDED.vacancy_url,
                published_at = EXCLUDED.published_at,
                collected_at = EXCLUDED.collected_at,
                is_active = TRUE,
                updated_at = NOW()
            RETURNING id
            """
        )
        result = connection.execute(
            query,
            {
                "source_name": vacancy.source_name,
                "source_vacancy_id": vacancy.source_vacancy_id,
                "role_id": role_id,
                "title": vacancy.title,
                "company_name": vacancy.company_name,
                "city": vacancy.city,
                "country": vacancy.country,
                "seniority_level": vacancy.seniority_level,
                "employment_type": vacancy.employment_type,
                "work_format": vacancy.work_format,
                "description_text": vacancy.description_text,
                "vacancy_url": vacancy.vacancy_url,
                "published_at": vacancy.published_at,
                "collected_at": vacancy.collected_at,
            },
        )
        return int(result.scalar_one())

    @staticmethod
    def _upsert_salary(connection: Any, vacancy_id: int, vacancy: NormalizedVacancy) -> None:
        from sqlalchemy import text

        if vacancy.salary is None:
            connection.execute(
                text("DELETE FROM salary_info WHERE vacancy_id = :vacancy_id"),
                {"vacancy_id": vacancy_id},
            )
            return

        query = text(
            """
            INSERT INTO salary_info (
                vacancy_id,
                salary_from,
                salary_to,
                currency_code,
                gross_type,
                salary_period
            )
            VALUES (
                :vacancy_id,
                :salary_from,
                :salary_to,
                :currency_code,
                :gross_type,
                :salary_period
            )
            ON CONFLICT (vacancy_id) DO UPDATE
            SET salary_from = EXCLUDED.salary_from,
                salary_to = EXCLUDED.salary_to,
                currency_code = EXCLUDED.currency_code,
                gross_type = EXCLUDED.gross_type,
                salary_period = EXCLUDED.salary_period
            """
        )
        connection.execute(
            query,
            {
                "vacancy_id": vacancy_id,
                "salary_from": vacancy.salary.salary_from,
                "salary_to": vacancy.salary.salary_to,
                "currency_code": vacancy.salary.currency_code,
                "gross_type": vacancy.salary.gross_type,
                "salary_period": vacancy.salary.salary_period,
            },
        )

    def _replace_skills(self, connection: Any, vacancy_id: int, vacancy: NormalizedVacancy) -> None:
        from sqlalchemy import text

        connection.execute(
            text("DELETE FROM vacancy_skills WHERE vacancy_id = :vacancy_id"),
            {"vacancy_id": vacancy_id},
        )

        for skill_match in vacancy.skills:
            skill_id = self._upsert_skill(connection, skill_match.definition)
            connection.execute(
                text(
                    """
                    INSERT INTO vacancy_skills (
                        vacancy_id,
                        skill_id,
                        is_required,
                        match_source
                    )
                    VALUES (
                        :vacancy_id,
                        :skill_id,
                        :is_required,
                        :match_source
                    )
                    """
                ),
                {
                    "vacancy_id": vacancy_id,
                    "skill_id": skill_id,
                    "is_required": skill_match.is_required,
                    "match_source": skill_match.match_source,
                },
            )

    @staticmethod
    def _upsert_skill(connection: Any, skill_definition: Any) -> int:
        from sqlalchemy import text

        query = text(
            """
            INSERT INTO skills (skill_name, skill_slug, skill_category)
            VALUES (:skill_name, :skill_slug, :skill_category)
            ON CONFLICT (skill_slug) DO UPDATE
            SET skill_name = EXCLUDED.skill_name,
                skill_category = EXCLUDED.skill_category
            RETURNING id
            """
        )
        result = connection.execute(
            query,
            {
                "skill_name": skill_definition.name,
                "skill_slug": skill_definition.slug,
                "skill_category": skill_definition.category,
            },
        )
        return int(result.scalar_one())

    @staticmethod
    def _upsert_raw_metadata(connection: Any, vacancy_id: int, vacancy: NormalizedVacancy) -> None:
        from sqlalchemy import text

        payload_json = json.dumps(vacancy.raw_payload, ensure_ascii=False, sort_keys=True)
        checksum = hashlib.sha256(payload_json.encode("utf-8")).hexdigest()

        query = text(
            """
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
            VALUES (
                :vacancy_id,
                :source_name,
                :source_url,
                CAST(:source_payload AS jsonb),
                :parser_version,
                :http_status,
                :checksum,
                :collected_at
            )
            ON CONFLICT (vacancy_id) DO UPDATE
            SET source_name = EXCLUDED.source_name,
                source_url = EXCLUDED.source_url,
                source_payload = EXCLUDED.source_payload,
                parser_version = EXCLUDED.parser_version,
                http_status = EXCLUDED.http_status,
                checksum = EXCLUDED.checksum,
                collected_at = EXCLUDED.collected_at
            """
        )
        connection.execute(
            query,
            {
                "vacancy_id": vacancy_id,
                "source_name": vacancy.source_name,
                "source_url": vacancy.vacancy_url,
                "source_payload": payload_json,
                "parser_version": "rule_based_v1",
                "http_status": 200,
                "checksum": checksum,
                "collected_at": vacancy.collected_at,
            },
        )


def run_ingestion(
    input_path: Path,
    source_name: str,
    db_engine: Engine | Any | None = None,
    dry_run: bool = False,
) -> IngestionResult:
    if source_name not in SOURCE_NAMES:
        raise ValueError(f"Unsupported source_name: {source_name}")

    records = load_source_records(input_path)
    collected_at = datetime.now(timezone.utc)

    valid_vacancies: list[NormalizedVacancy] = []
    errors: list[str] = []

    for index, record in enumerate(records, start=1):
        validation_errors = validate_required_fields(record)
        if validation_errors:
            record_id = get_field_value(record, "source_vacancy_id") or f"row_{index}"
            errors.append(f"{record_id}: {', '.join(validation_errors)}")
            continue

        valid_vacancies.append(
            normalize_record(
                record=record,
                source_name=source_name,
                collected_at=collected_at,
            )
        )

    loaded_records = 0
    if not dry_run and valid_vacancies:
        writer = PostgresIngestionWriter(db_engine or get_default_engine())
        loaded_records = writer.write(valid_vacancies)

    return IngestionResult(
        total_records=len(records),
        valid_records=len(valid_vacancies),
        invalid_records=len(errors),
        loaded_records=loaded_records,
        errors=errors,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Load prepared vacancy data from JSON or CSV into PostgreSQL."
    )
    parser.add_argument("--input", required=True, help="Path to local JSON or CSV file.")
    parser.add_argument(
        "--source",
        default="manual",
        choices=sorted(SOURCE_NAMES),
        help="Logical source name for loaded vacancies.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and normalize records without writing to PostgreSQL.",
    )
    args = parser.parse_args()

    result = run_ingestion(
        input_path=Path(args.input),
        source_name=args.source,
        dry_run=args.dry_run,
    )

    print(
        json.dumps(
            {
                "total_records": result.total_records,
                "valid_records": result.valid_records,
                "invalid_records": result.invalid_records,
                "loaded_records": result.loaded_records,
                "errors": result.errors,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
