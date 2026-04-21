from pathlib import Path

from sqlalchemy import create_engine

from app.core.config import settings

BASE_DIR = Path(__file__).resolve().parents[2]
SQL_DIR = BASE_DIR / "sql"
SCHEMA_FILE = SQL_DIR / "01_init_schema.sql"
SEED_FILE = SQL_DIR / "02_seed_data.sql"


def _load_sql(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def apply_sql_file(path: Path) -> None:
    engine = create_engine(settings.database_url, future=True)
    sql = _load_sql(path)

    with engine.begin() as connection:
        raw_connection = connection.connection
        raw_connection.cursor().execute(sql)


def init_schema() -> None:
    apply_sql_file(SCHEMA_FILE)


def seed_data() -> None:
    apply_sql_file(SEED_FILE)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Initialize PostgreSQL schema and optional seed data."
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Load seed data after schema initialization.",
    )
    args = parser.parse_args()

    init_schema()

    if args.seed:
        seed_data()
