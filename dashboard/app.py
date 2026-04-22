from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from dashboard.api_client import DashboardApiClient
from dashboard.api_client import DashboardApiError

st.set_page_config(page_title="IT Skills Radar", page_icon="📊", layout="wide")

API_URL = os.getenv("API_URL", "http://localhost:8000")
DEFAULT_SENIORITY = ["junior", "intern"]


@st.cache_data(ttl=60)
def fetch_roles(api_url: str) -> list[dict]:
    return DashboardApiClient(api_url).get_roles()


@st.cache_data(ttl=60)
def fetch_top_skills(api_url: str, role_code: str | None, seniority_levels: tuple[str, ...]) -> list[dict]:
    return DashboardApiClient(api_url).get_top_skills(
        role_code=role_code,
        seniority_levels=list(seniority_levels),
        rank_limit=10,
    )


@st.cache_data(ttl=60)
def fetch_skill_trends(
    api_url: str,
    skill_slug: str | None,
    role_code: str | None,
    seniority_levels: tuple[str, ...],
) -> list[dict]:
    return DashboardApiClient(api_url).get_skill_trends(
        skill_slug=skill_slug,
        role_code=role_code,
        seniority_levels=list(seniority_levels),
    )


@st.cache_data(ttl=60)
def fetch_salary_premium(
    api_url: str,
    skill_slug: str | None,
    role_code: str | None,
    seniority_levels: tuple[str, ...],
) -> list[dict]:
    return DashboardApiClient(api_url).get_salary_premium(
        skill_slug=skill_slug,
        role_code=role_code,
        seniority_levels=list(seniority_levels),
    )


@st.cache_data(ttl=60)
def fetch_junior_overview(api_url: str) -> list[dict]:
    return DashboardApiClient(api_url).get_junior_overview()


def format_share(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value * 100:.1f}%"


def format_money(value: float | None) -> str:
    if value is None:
        return "n/a"
    return f"{value:,.0f} RUB".replace(",", " ")


st.title("IT Skills Radar")
st.caption("MVP dashboard over precomputed analytics views. Data comes from the FastAPI layer, while metrics are calculated in PostgreSQL views.")

try:
    roles = fetch_roles(API_URL)
except DashboardApiError as exc:
    st.error(str(exc))
    st.stop()

role_options = [{"role_code": "", "role_name": "All roles"}] + roles
role_labels = [item["role_name"] for item in role_options]
selected_role_label = st.sidebar.selectbox("Role", role_labels, index=0)
selected_role = next(item for item in role_options if item["role_name"] == selected_role_label)

selected_seniority = st.sidebar.multiselect(
    "Seniority",
    options=["intern", "junior", "middle", "senior", "lead", "unknown"],
    default=DEFAULT_SENIORITY,
)

selected_role_code = selected_role["role_code"] or None
selected_seniority_tuple = tuple(selected_seniority)

try:
    top_skills = fetch_top_skills(API_URL, selected_role_code, selected_seniority_tuple)
    junior_overview = fetch_junior_overview(API_URL)
except DashboardApiError as exc:
    st.error(str(exc))
    st.stop()

skill_options = sorted({item["skill_name"]: item["skill_slug"] for item in top_skills}.items())
default_skill_label = skill_options[0][0] if skill_options else None
selected_skill_label = st.sidebar.selectbox(
    "Trend skill",
    options=[label for label, _ in skill_options] if skill_options else ["No skills available"],
    index=0,
)
selected_skill_slug = None
for label, slug in skill_options:
    if label == selected_skill_label:
        selected_skill_slug = slug
        break

try:
    skill_trends = fetch_skill_trends(
        API_URL,
        selected_skill_slug,
        selected_role_code,
        selected_seniority_tuple,
    )
    salary_premium = fetch_salary_premium(
        API_URL,
        selected_skill_slug,
        selected_role_code,
        selected_seniority_tuple,
    )
except DashboardApiError as exc:
    st.error(str(exc))
    st.stop()

overview_by_role = {item["role_code"]: item for item in junior_overview}
selected_overview = overview_by_role.get(selected_role_code or "")
summary_top_skill = top_skills[0] if top_skills else None
summary_salary = salary_premium[0] if salary_premium else None

col1, col2, col3 = st.columns(3)
with col1:
    st.metric(
        "Top skill",
        summary_top_skill["skill_name"] if summary_top_skill else "n/a",
        format_share(summary_top_skill["vacancy_share"]) if summary_top_skill else None,
    )
with col2:
    st.metric(
        "Best salary signal",
        summary_salary["skill_name"] if summary_salary else "n/a",
        format_money(summary_salary["salary_premium_abs"]) if summary_salary else None,
    )
with col3:
    st.metric(
        "Junior median salary",
        format_money(selected_overview["median_salary_mid"]) if selected_overview else "n/a",
        format_share(selected_overview["salary_coverage"]) if selected_overview else None,
    )

st.subheader("Summary")
if summary_top_skill:
    st.write(
        f"For the current filter, the strongest demand signal is **{summary_top_skill['skill_name']}** "
        f"with presence in **{format_share(summary_top_skill['vacancy_share'])}** of vacancies."
    )
if summary_salary:
    st.write(
        f"The clearest salary premium signal is **{summary_salary['skill_name']}**, "
        f"with median salary difference around **{format_money(summary_salary['salary_premium_abs'])}**."
    )
if not summary_top_skill and not summary_salary:
    st.info("No analytics data matched the current filter.")

left_col, right_col = st.columns([1.2, 1])

with left_col:
    st.subheader("Top Skills")
    if top_skills:
        top_skills_df = pd.DataFrame(top_skills)[
            ["skill_rank", "skill_name", "vacancy_count", "vacancy_share", "seniority_level"]
        ].rename(
            columns={
                "skill_rank": "Rank",
                "skill_name": "Skill",
                "vacancy_count": "Vacancies",
                "vacancy_share": "Share",
                "seniority_level": "Seniority",
            }
        )
        top_skills_df["Share"] = top_skills_df["Share"].map(format_share)
        st.dataframe(top_skills_df, use_container_width=True, hide_index=True)
    else:
        st.info("No top skills available for the selected filter.")

    st.subheader("Skill Trend Over Time")
    if skill_trends:
        trend_df = pd.DataFrame(skill_trends)
        trend_chart_df = trend_df[["month_start", "vacancy_share"]].copy()
        trend_chart_df["month_start"] = pd.to_datetime(trend_chart_df["month_start"])
        trend_chart_df = trend_chart_df.sort_values("month_start").set_index("month_start")
        st.line_chart(trend_chart_df, height=280)

        trend_table = trend_df[["month_start", "skill_name", "vacancy_count", "vacancy_share"]].rename(
            columns={
                "month_start": "Month",
                "skill_name": "Skill",
                "vacancy_count": "Vacancies",
                "vacancy_share": "Share",
            }
        )
        trend_table["Share"] = trend_table["Share"].map(format_share)
        st.dataframe(trend_table, use_container_width=True, hide_index=True)
    else:
        st.info("No trend data available for the selected skill.")

with right_col:
    st.subheader("Salary Premium")
    if salary_premium:
        salary_df = pd.DataFrame(salary_premium)[
            [
                "skill_name",
                "vacancies_with_skill",
                "vacancies_without_skill",
                "median_salary_with_skill",
                "median_salary_without_skill",
                "salary_premium_abs",
                "salary_premium_pct",
            ]
        ].rename(
            columns={
                "skill_name": "Skill",
                "vacancies_with_skill": "With skill",
                "vacancies_without_skill": "Without skill",
                "median_salary_with_skill": "Median with",
                "median_salary_without_skill": "Median without",
                "salary_premium_abs": "Premium abs",
                "salary_premium_pct": "Premium pct",
            }
        )
        for column_name in ["Median with", "Median without", "Premium abs"]:
            salary_df[column_name] = salary_df[column_name].map(format_money)
        salary_df["Premium pct"] = salary_df["Premium pct"].map(format_share)
        st.dataframe(salary_df, use_container_width=True, hide_index=True)
    else:
        st.info("No salary premium data available for the current filter.")

    st.subheader("Junior / Intern Overview")
    if junior_overview:
        overview_df = pd.DataFrame(junior_overview)[
            [
                "role_name",
                "seniority_level",
                "total_vacancies",
                "salary_coverage",
                "median_salary_mid",
            ]
        ].rename(
            columns={
                "role_name": "Role",
                "seniority_level": "Seniority",
                "total_vacancies": "Vacancies",
                "salary_coverage": "Salary coverage",
                "median_salary_mid": "Median salary",
            }
        )
        overview_df["Salary coverage"] = overview_df["Salary coverage"].map(format_share)
        overview_df["Median salary"] = overview_df["Median salary"].map(format_money)
        st.dataframe(overview_df, use_container_width=True, hide_index=True)
    else:
        st.info("No junior overview data available.")

with st.expander("How the MVP is wired"):
    st.write(
        "- FastAPI returns rows from precomputed analytics views.\n"
        "- PostgreSQL computes metrics like skill share, monthly trend and salary premium.\n"
        "- Streamlit only requests filtered aggregates and renders tables/charts."
    )
    st.code(API_URL)
