from fastapi.testclient import TestClient

from app.api.dependencies import get_analytics_service
from app.main import app


class FakeAnalyticsService:
    def get_roles(self) -> list[dict]:
        return [{"role_code": "data_scientist", "role_name": "Data Scientist"}]

    def get_top_skills_by_role(self, **kwargs) -> list[dict]:
        return [
            {
                "role_code": "data_scientist",
                "role_name": "Data Scientist",
                "seniority_level": "junior",
                "skill_slug": "python",
                "skill_name": "Python",
                "vacancy_count": 3,
                "vacancy_share": 0.75,
                "skill_rank": 1,
            }
        ]

    def get_skills_trend_monthly(self, **kwargs) -> list[dict]:
        return [
            {
                "month_start": "2026-04-01",
                "role_code": "data_scientist",
                "role_name": "Data Scientist",
                "seniority_level": "junior",
                "skill_slug": "python",
                "skill_name": "Python",
                "vacancy_count": 3,
                "vacancy_share": 0.75,
            }
        ]

    def get_skill_salary_premium(self, **kwargs) -> list[dict]:
        return [
            {
                "role_code": "data_scientist",
                "role_name": "Data Scientist",
                "seniority_level": "junior",
                "skill_slug": "python",
                "skill_name": "Python",
                "vacancies_with_skill": 3,
                "vacancies_without_skill": 2,
                "median_salary_with_skill": 180000,
                "median_salary_without_skill": 150000,
                "salary_premium_abs": 30000,
                "salary_premium_pct": 0.2,
            }
        ]

    def get_junior_roles_overview(self) -> list[dict]:
        return [
            {
                "role_code": "data_scientist",
                "role_name": "Data Scientist",
                "seniority_level": "junior",
                "total_vacancies": 4,
                "salary_vacancies": 3,
                "salary_coverage": 0.75,
                "median_salary_mid": 165000,
                "average_salary_mid": 170000,
            }
        ]


app.dependency_overrides[get_analytics_service] = FakeAnalyticsService
client = TestClient(app)


def test_health_endpoint_returns_ok() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_roles_endpoint_returns_items() -> None:
    response = client.get("/roles")

    assert response.status_code == 200
    assert response.json()[0]["role_code"] == "data_scientist"


def test_top_skills_endpoint_returns_items() -> None:
    response = client.get("/skills/top", params={"role_code": "data_scientist"})

    assert response.status_code == 200
    assert response.json()[0]["skill_name"] == "Python"


def test_skills_trends_endpoint_returns_items() -> None:
    response = client.get("/skills/trends", params={"skill_slug": "python"})

    assert response.status_code == 200
    assert response.json()[0]["skill_slug"] == "python"


def test_salary_premium_endpoint_returns_items() -> None:
    response = client.get("/salary/premium", params={"skill_slug": "python"})

    assert response.status_code == 200
    assert response.json()[0]["salary_premium_pct"] == 0.2


def test_junior_overview_endpoint_returns_items() -> None:
    response = client.get("/overview/junior")

    assert response.status_code == 200
    assert response.json()[0]["total_vacancies"] == 4
