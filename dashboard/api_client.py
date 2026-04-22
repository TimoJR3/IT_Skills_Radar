from __future__ import annotations

from typing import Any

import httpx


class DashboardApiError(RuntimeError):
    pass


class DashboardApiClient:
    def __init__(self, base_url: str, timeout: float = 20.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str, params: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        url = f"{self.base_url}{path}"
        try:
            response = httpx.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise DashboardApiError(f"Не удалось загрузить данные {path}: {exc}") from exc

        payload = response.json()
        if not isinstance(payload, list):
            raise DashboardApiError(f"API вернул неожиданный формат ответа для {path}.")
        return payload

    def get_roles(self) -> list[dict[str, Any]]:
        return self._get("/roles")

    def get_top_skills(
        self,
        role_code: str | None,
        seniority_levels: list[str],
        rank_limit: int = 10,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"rank_limit": rank_limit}
        if role_code:
            params["role_code"] = role_code
        if seniority_levels:
            params["seniority_levels"] = seniority_levels
        return self._get("/skills/top", params=params)

    def get_skill_trends(
        self,
        skill_slug: str | None,
        role_code: str | None,
        seniority_levels: list[str],
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if skill_slug:
            params["skill_slug"] = skill_slug
        if role_code:
            params["role_code"] = role_code
        if seniority_levels:
            params["seniority_levels"] = seniority_levels
        return self._get("/skills/trends", params=params)

    def get_salary_premium(
        self,
        skill_slug: str | None,
        role_code: str | None,
        seniority_levels: list[str],
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {}
        if skill_slug:
            params["skill_slug"] = skill_slug
        if role_code:
            params["role_code"] = role_code
        if seniority_levels:
            params["seniority_levels"] = seniority_levels
        return self._get("/salary/premium", params=params)

    def get_junior_overview(self) -> list[dict[str, Any]]:
        return self._get("/overview/junior")
