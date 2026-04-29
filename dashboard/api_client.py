from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class ApiResult:
    endpoint: str
    ok: bool
    status_code: int | None
    data: Any
    message: str

    @property
    def rows_count(self) -> int:
        if isinstance(self.data, list):
            return len(self.data)
        return 0


class DashboardApiError(RuntimeError):
    def __init__(
        self,
        message: str,
        endpoint: str,
        status_code: int | None = None,
    ) -> None:
        super().__init__(message)
        self.endpoint = endpoint
        self.status_code = status_code


class DashboardApiClient:
    def __init__(self, base_url: str, timeout: float = 20.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def request_json(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> ApiResult:
        url = f"{self.base_url}{path}"
        try:
            response = httpx.get(url, params=params, timeout=self.timeout)
        except httpx.RequestError as exc:
            return ApiResult(
                endpoint=path,
                ok=False,
                status_code=None,
                data=None,
                message=(
                    f"API недоступен: не удалось выполнить запрос к {path}. "
                    f"Проверьте Docker Compose и адрес {self.base_url}."
                ),
            )

        try:
            payload = response.json()
        except ValueError:
            payload = None

        if response.status_code >= 400:
            detail = _extract_detail(payload)
            return ApiResult(
                endpoint=path,
                ok=False,
                status_code=response.status_code,
                data=payload,
                message=(
                    f"Маршрут {path} вернул {response.status_code}. "
                    f"{detail}"
                ).strip(),
            )

        return ApiResult(
            endpoint=path,
            ok=True,
            status_code=response.status_code,
            data=payload,
            message="OK",
        )

    def request_list(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> ApiResult:
        result = self.request_json(path, params=params)
        if not result.ok:
            return result
        if not isinstance(result.data, list):
            return ApiResult(
                endpoint=path,
                ok=False,
                status_code=result.status_code,
                data=result.data,
                message=f"API вернул неожиданный формат ответа для {path}.",
            )
        return result

    def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        result = self.request_list(path, params=params)
        if not result.ok:
            raise DashboardApiError(
                message=f"Не удалось загрузить данные {path}: {result.message}",
                endpoint=path,
                status_code=result.status_code,
            )
        return result.data

    def get_roles(self) -> list[dict[str, Any]]:
        return self._get("/roles")

    def get_top_skills(
        self,
        role_code: str | None,
        seniority_levels: list[str],
        rank_limit: int = 10,
    ) -> list[dict[str, Any]]:
        return self._get(
            "/skills/top",
            params=_analytics_params(role_code, seniority_levels, rank_limit),
        )

    def get_skill_trends(
        self,
        skill_slug: str | None,
        role_code: str | None,
        seniority_levels: list[str],
    ) -> list[dict[str, Any]]:
        params = _analytics_params(role_code, seniority_levels)
        if skill_slug:
            params["skill_slug"] = skill_slug
        return self._get("/skills/trends", params=params)

    def get_salary_premium(
        self,
        skill_slug: str | None,
        role_code: str | None,
        seniority_levels: list[str],
    ) -> list[dict[str, Any]]:
        params = _analytics_params(role_code, seniority_levels)
        if skill_slug:
            params["skill_slug"] = skill_slug
        return self._get("/salary/premium", params=params)

    def get_junior_overview(self) -> list[dict[str, Any]]:
        return self._get("/overview/junior")


def _analytics_params(
    role_code: str | None,
    seniority_levels: list[str],
    rank_limit: int | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if role_code:
        params["role_code"] = role_code
    if seniority_levels:
        params["seniority_levels"] = seniority_levels
    if rank_limit is not None:
        params["rank_limit"] = rank_limit
    return params


def _extract_detail(payload: Any) -> str:
    if isinstance(payload, dict):
        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail
    return "Подробности недоступны."
