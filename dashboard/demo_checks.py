from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dashboard.api_client import ApiResult


@dataclass(frozen=True)
class DemoCheck:
    name: str
    endpoint: str
    status: str
    message: str
    rows_count: int | None = None


STATUS_LABELS = {
    "success": "УСПЕХ",
    "warning": "ПРЕДУПРЕЖДЕНИЕ",
    "error": "ОШИБКА",
}


def status_label(status: str) -> str:
    return STATUS_LABELS.get(status, "ПРЕДУПРЕЖДЕНИЕ")


def normalize_demo_check(
    name: str,
    result: ApiResult,
    success_message: str,
    empty_message: str,
) -> DemoCheck:
    if not result.ok:
        return DemoCheck(
            name=name,
            endpoint=result.endpoint,
            status="error",
            message=_endpoint_error_message(result),
            rows_count=result.rows_count,
        )

    if isinstance(result.data, list) and not result.data:
        return DemoCheck(
            name=name,
            endpoint=result.endpoint,
            status="warning",
            message=empty_message,
            rows_count=0,
        )

    return DemoCheck(
        name=name,
        endpoint=result.endpoint,
        status="success",
        message=success_message,
        rows_count=result.rows_count,
    )


def database_check_from_results(results: list[ApiResult]) -> DemoCheck:
    roles = _find_result(results, "/roles")
    top_skills = _find_result(results, "/skills/top")
    if roles and roles.ok and roles.rows_count > 0:
        return DemoCheck(
            name="База данных",
            endpoint="/roles",
            status="success",
            message="УСПЕХ: база данных инициализирована",
            rows_count=roles.rows_count,
        )
    if top_skills and top_skills.ok and top_skills.rows_count > 0:
        return DemoCheck(
            name="База данных",
            endpoint="/skills/top",
            status="success",
            message="УСПЕХ: демо-данные загружены",
            rows_count=top_skills.rows_count,
        )
    return DemoCheck(
        name="База данных",
        endpoint="/roles",
        status="error",
        message="ОШИБКА: база данных не инициализирована или роли не загружены",
        rows_count=0,
    )


def analytics_views_check_from_results(results: list[ApiResult]) -> DemoCheck:
    analytics_results = [
        item
        for item in results
        if item.endpoint in {"/skills/top", "/skills/trends", "/salary/premium"}
    ]
    if analytics_results and all(item.ok for item in analytics_results):
        return DemoCheck(
            name="SQL-витрины",
            endpoint="analytics.*",
            status="success",
            message="УСПЕХ: аналитические витрины доступны",
            rows_count=sum(item.rows_count for item in analytics_results),
        )
    return DemoCheck(
        name="SQL-витрины",
        endpoint="analytics.*",
        status="error",
        message="ОШИБКА: база данных не инициализирована или витрины недоступны",
        rows_count=0,
    )


def sample_data_check_from_results(results: list[ApiResult]) -> DemoCheck:
    top_skills = _find_result(results, "/skills/top")
    junior = _find_result(results, "/overview/junior")
    rows_count = (top_skills.rows_count if top_skills else 0) + (
        junior.rows_count if junior else 0
    )
    if rows_count > 0:
        return DemoCheck(
            name="Демо-данные",
            endpoint="/skills/top + /overview/junior",
            status="success",
            message="УСПЕХ: демо-данные загружены",
            rows_count=rows_count,
        )
    return DemoCheck(
        name="Демо-данные",
        endpoint="/skills/top + /overview/junior",
        status="warning",
        message="ПРЕДУПРЕЖДЕНИЕ: демо-данные пока не загружены",
        rows_count=0,
    )


def checks_to_rows(checks: list[DemoCheck]) -> list[dict[str, Any]]:
    return [
        {
            "Проверка": check.name,
            "Маршрут": check.endpoint,
            "Статус": status_label(check.status),
            "Сообщение": check.message,
            "Строк": check.rows_count,
        }
        for check in checks
    ]


def _endpoint_error_message(result: ApiResult) -> str:
    if result.status_code == 500:
        return f"ОШИБКА: маршрут {result.endpoint} вернул 500"
    if result.status_code == 503:
        return "ОШИБКА: база данных не инициализирована или витрины недоступны"
    if result.status_code is None:
        return f"ОШИБКА: маршрут {result.endpoint} недоступен"
    return f"ОШИБКА: маршрут {result.endpoint} вернул {result.status_code}"


def _find_result(results: list[ApiResult], endpoint: str) -> ApiResult | None:
    for result in results:
        if result.endpoint == endpoint:
            return result
    return None
