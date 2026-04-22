from __future__ import annotations

from typing import Any
from typing import Callable

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Query

from app.api.dependencies import get_analytics_service
from app.schemas.analytics import JuniorOverviewItem
from app.schemas.analytics import RoleItem
from app.schemas.analytics import SalaryPremiumItem
from app.schemas.analytics import SkillTrendItem
from app.schemas.analytics import TopSkillItem
from app.schemas.health import HealthResponse
from app.services.analytics import AnalyticsService

router = APIRouter()


def _safe_call(operation: str, func: Callable[[], list[dict[str, Any]]]) -> list[dict[str, Any]]:
    try:
        return func()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Сервис аналитики недоступен для операции '{operation}': {exc}",
        ) from exc
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=500,
            detail=f"Не удалось получить данные для операции '{operation}'.",
        ) from exc


@router.get(
    "/health",
    response_model=HealthResponse,
    tags=["health"],
    summary="Проверка доступности сервиса",
)
def healthcheck() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get(
    "/roles",
    response_model=list[RoleItem],
    tags=["analytics"],
    summary="Список ролей",
    description="Возвращает список нормализованных ролей для фильтров UI.",
)
def get_roles(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> list[RoleItem]:
    result = _safe_call("список ролей", analytics_service.get_roles)
    return [RoleItem(**item) for item in result]


@router.get(
    "/skills/top",
    response_model=list[TopSkillItem],
    tags=["analytics"],
    summary="Топ навыков по роли",
    description="Возвращает самые частые навыки по выбранной роли и уровню.",
)
def get_top_skills(
    role_code: str | None = Query(default=None, description="Код роли, например data_scientist"),
    seniority_levels: list[str] | None = Query(default=None, description="Список уровней seniority"),
    rank_limit: int = Query(default=10, ge=1, le=30, description="Максимум строк в выдаче"),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> list[TopSkillItem]:
    result = _safe_call(
        "топ навыков",
        lambda: analytics_service.get_top_skills_by_role(
            role_code=role_code,
            seniority_levels=seniority_levels,
            rank_limit=rank_limit,
        ),
    )
    return [TopSkillItem(**item) for item in result]


@router.get(
    "/skills/trends",
    response_model=list[SkillTrendItem],
    tags=["analytics"],
    summary="Динамика навыков по месяцам",
    description="Возвращает помесячную динамику упоминаний навыка.",
)
def get_skill_trends(
    skill_slug: str | None = Query(default=None, description="Slug навыка, например python"),
    role_code: str | None = Query(default=None, description="Код роли"),
    seniority_levels: list[str] | None = Query(default=None, description="Список уровней seniority"),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> list[SkillTrendItem]:
    result = _safe_call(
        "динамика навыков",
        lambda: analytics_service.get_skills_trend_monthly(
            skill_slug=skill_slug,
            role_code=role_code,
            seniority_levels=seniority_levels,
        ),
    )
    return [SkillTrendItem(**item) for item in result]


@router.get(
    "/salary/premium",
    response_model=list[SalaryPremiumItem],
    tags=["analytics"],
    summary="Премия к зарплате по навыкам",
    description="Сравнивает медианную зарплату вакансий с навыком и без навыка.",
)
def get_salary_premium(
    skill_slug: str | None = Query(default=None, description="Slug навыка"),
    role_code: str | None = Query(default=None, description="Код роли"),
    seniority_levels: list[str] | None = Query(default=None, description="Список уровней seniority"),
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> list[SalaryPremiumItem]:
    result = _safe_call(
        "премия к зарплате",
        lambda: analytics_service.get_skill_salary_premium(
            skill_slug=skill_slug,
            role_code=role_code,
            seniority_levels=seniority_levels,
        ),
    )
    return [SalaryPremiumItem(**item) for item in result]


@router.get(
    "/overview/junior",
    response_model=list[JuniorOverviewItem],
    tags=["analytics"],
    summary="Обзор junior и intern ролей",
    description="Возвращает краткий срез по entry-level ролям и зарплатам.",
)
def get_junior_overview(
    analytics_service: AnalyticsService = Depends(get_analytics_service),
) -> list[JuniorOverviewItem]:
    result = _safe_call("обзор junior ролей", analytics_service.get_junior_roles_overview)
    return [JuniorOverviewItem(**item) for item in result]
