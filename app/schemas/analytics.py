from datetime import date

from pydantic import BaseModel


class RoleItem(BaseModel):
    role_code: str
    role_name: str


class TopSkillItem(BaseModel):
    role_code: str
    role_name: str
    seniority_level: str
    skill_slug: str
    skill_name: str
    vacancy_count: int
    vacancy_share: float | None
    skill_rank: int


class SkillTrendItem(BaseModel):
    month_start: date
    role_code: str
    role_name: str
    seniority_level: str
    skill_slug: str
    skill_name: str
    vacancy_count: int
    vacancy_share: float | None


class SalaryPremiumItem(BaseModel):
    role_code: str
    role_name: str
    seniority_level: str
    skill_slug: str
    skill_name: str
    vacancies_with_skill: int
    vacancies_without_skill: int
    median_salary_with_skill: float | None
    median_salary_without_skill: float | None
    salary_premium_abs: float | None
    salary_premium_pct: float | None


class RoleSkillDistributionItem(BaseModel):
    role_code: str
    role_name: str
    seniority_level: str
    skill_slug: str
    skill_name: str
    vacancy_count: int
    skill_penetration_in_role: float | None
    role_share_of_skill: float | None
    required_share: float | None


class JuniorOverviewItem(BaseModel):
    role_code: str
    role_name: str
    seniority_level: str
    total_vacancies: int
    salary_vacancies: int
    salary_coverage: float | None
    median_salary_mid: float | None
    average_salary_mid: float | None
