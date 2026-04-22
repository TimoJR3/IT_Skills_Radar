from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine


def calculate_share(numerator: int | float, denominator: int | float) -> float | None:
    if denominator == 0:
        return None
    return round(float(numerator) / float(denominator), 4)


def calculate_salary_premium_pct(
    median_with_skill: Decimal | float | None,
    median_without_skill: Decimal | float | None,
) -> float | None:
    if median_with_skill is None or median_without_skill in (None, 0):
        return None
    return round(
        (float(median_with_skill) - float(median_without_skill))
        / float(median_without_skill),
        4,
    )


def get_default_engine() -> Any:
    try:
        from app.db.session import engine
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Database dependencies are not installed. Run pip install -r requirements.txt first."
        ) from exc

    return engine


def _add_list_filter(
    clauses: list[str],
    params: dict[str, Any],
    column_name: str,
    values: list[str] | None,
    key_prefix: str,
) -> None:
    if not values:
        return

    placeholders: list[str] = []
    for index, value in enumerate(values):
        key = f"{key_prefix}_{index}"
        params[key] = value
        placeholders.append(f":{key}")

    clauses.append(f"{column_name} IN ({', '.join(placeholders)})")


def _rows_to_dicts(result: Any) -> list[dict[str, Any]]:
    return [dict(row._mapping) for row in result]


class AnalyticsService:
    def __init__(self, db_engine: Engine | Any | None = None) -> None:
        self.engine = db_engine or get_default_engine()

    def get_roles(self) -> list[dict[str, Any]]:
        from sqlalchemy import text

        query = text(
            """
            SELECT role_code, role_name
            FROM roles
            ORDER BY role_name
            """
        )
        with self.engine.begin() as connection:
            return _rows_to_dicts(connection.execute(query))

    def get_top_skills_by_role(
        self,
        role_code: str | None = None,
        seniority_levels: list[str] | None = None,
        rank_limit: int = 10,
    ) -> list[dict[str, Any]]:
        from sqlalchemy import text

        clauses = ["skill_rank <= :rank_limit"]
        params: dict[str, Any] = {"rank_limit": rank_limit}

        if role_code:
            clauses.append("role_code = :role_code")
            params["role_code"] = role_code

        _add_list_filter(
            clauses=clauses,
            params=params,
            column_name="seniority_level",
            values=seniority_levels,
            key_prefix="seniority",
        )

        query = text(
            f"""
            SELECT *
            FROM analytics.top_skills_by_role
            WHERE {' AND '.join(clauses)}
            ORDER BY role_code, seniority_level, skill_rank
            """
        )
        with self.engine.begin() as connection:
            return _rows_to_dicts(connection.execute(query, params))

    def get_skills_trend_monthly(
        self,
        skill_slug: str | None = None,
        role_code: str | None = None,
        seniority_levels: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        from sqlalchemy import text

        clauses = ["1 = 1"]
        params: dict[str, Any] = {}

        if skill_slug:
            clauses.append("skill_slug = :skill_slug")
            params["skill_slug"] = skill_slug

        if role_code:
            clauses.append("role_code = :role_code")
            params["role_code"] = role_code

        _add_list_filter(
            clauses=clauses,
            params=params,
            column_name="seniority_level",
            values=seniority_levels,
            key_prefix="seniority",
        )

        query = text(
            f"""
            SELECT *
            FROM analytics.skills_trend_monthly
            WHERE {' AND '.join(clauses)}
            ORDER BY month_start, role_code, seniority_level, vacancy_count DESC, skill_name
            """
        )
        with self.engine.begin() as connection:
            return _rows_to_dicts(connection.execute(query, params))

    def get_skill_salary_premium(
        self,
        skill_slug: str | None = None,
        role_code: str | None = None,
        seniority_levels: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        from sqlalchemy import text

        clauses = ["1 = 1"]
        params: dict[str, Any] = {}

        if skill_slug:
            clauses.append("skill_slug = :skill_slug")
            params["skill_slug"] = skill_slug

        if role_code:
            clauses.append("role_code = :role_code")
            params["role_code"] = role_code

        _add_list_filter(
            clauses=clauses,
            params=params,
            column_name="seniority_level",
            values=seniority_levels,
            key_prefix="seniority",
        )

        query = text(
            f"""
            SELECT *
            FROM analytics.skill_salary_premium
            WHERE {' AND '.join(clauses)}
            ORDER BY role_code, seniority_level, salary_premium_abs DESC, skill_name
            """
        )
        with self.engine.begin() as connection:
            return _rows_to_dicts(connection.execute(query, params))

    def get_role_skill_distribution(
        self,
        role_code: str | None = None,
        skill_slug: str | None = None,
        seniority_levels: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        from sqlalchemy import text

        clauses = ["1 = 1"]
        params: dict[str, Any] = {}

        if role_code:
            clauses.append("role_code = :role_code")
            params["role_code"] = role_code

        if skill_slug:
            clauses.append("skill_slug = :skill_slug")
            params["skill_slug"] = skill_slug

        _add_list_filter(
            clauses=clauses,
            params=params,
            column_name="seniority_level",
            values=seniority_levels,
            key_prefix="seniority",
        )

        query = text(
            f"""
            SELECT *
            FROM analytics.role_skill_distribution
            WHERE {' AND '.join(clauses)}
            ORDER BY skill_name, role_share_of_skill DESC, role_code
            """
        )
        with self.engine.begin() as connection:
            return _rows_to_dicts(connection.execute(query, params))

    def get_junior_roles_overview(self) -> list[dict[str, Any]]:
        from sqlalchemy import text

        query = text(
            """
            SELECT *
            FROM analytics.junior_roles_overview
            ORDER BY seniority_level, total_vacancies DESC, role_code
            """
        )
        with self.engine.begin() as connection:
            return _rows_to_dicts(connection.execute(query))
