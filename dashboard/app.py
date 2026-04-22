from __future__ import annotations

import os

import pandas as pd
import streamlit as st

from api_client import DashboardApiClient
from api_client import DashboardApiError

st.set_page_config(page_title="IT Skills Radar", page_icon="📈", layout="wide")

API_URL = os.getenv("API_URL", "http://localhost:8000")
DEFAULT_SENIORITY = ["junior", "intern"]
SENIORITY_OPTIONS = ["intern", "junior", "middle", "senior", "lead", "unknown"]
SENIORITY_LABELS = {
    "intern": "Стажер",
    "junior": "Junior",
    "middle": "Middle",
    "senior": "Senior",
    "lead": "Lead",
    "unknown": "Не указан",
}
ROLE_LABELS = {
    "data_scientist": "Data Scientist",
    "data_analyst": "Data Analyst",
    "product_analyst": "Product Analyst",
    "ml_engineer": "ML Engineer",
    "other_data_role": "Смежная data/product роль",
}

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Manrope', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at top left, rgba(196, 230, 255, 0.65), transparent 30%),
                radial-gradient(circle at top right, rgba(255, 229, 194, 0.55), transparent 28%),
                linear-gradient(180deg, #f7f3eb 0%, #f2f7fb 100%);
        }

        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #12343b 0%, #204f58 100%);
            border-right: 1px solid rgba(255,255,255,0.08);
        }

        section[data-testid="stSidebar"] * {
            color: #f5f7f8;
        }

        .hero-card {
            padding: 1.5rem 1.6rem;
            border-radius: 24px;
            background: linear-gradient(135deg, #12343b 0%, #265d66 52%, #d97a32 100%);
            color: #ffffff;
            box-shadow: 0 20px 60px rgba(18, 52, 59, 0.22);
            margin-bottom: 1rem;
        }

        .hero-eyebrow {
            font-size: 0.82rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            opacity: 0.82;
            margin-bottom: 0.5rem;
        }

        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            line-height: 1.05;
            margin: 0 0 0.7rem 0;
        }

        .hero-text {
            max-width: 900px;
            font-size: 1rem;
            line-height: 1.6;
            opacity: 0.95;
            margin: 0;
        }

        .metric-card {
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid rgba(18, 52, 59, 0.08);
            border-radius: 18px;
            padding: 1rem 1rem 0.95rem 1rem;
            box-shadow: 0 14px 36px rgba(36, 53, 62, 0.08);
            min-height: 132px;
        }

        .metric-label {
            font-size: 0.84rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #5a6f74;
            margin-bottom: 0.5rem;
        }

        .metric-value {
            font-size: 1.5rem;
            font-weight: 800;
            color: #12343b;
            line-height: 1.15;
            margin-bottom: 0.35rem;
        }

        .metric-subvalue {
            font-size: 0.95rem;
            color: #425b61;
            line-height: 1.4;
        }

        .section-card {
            background: rgba(255, 255, 255, 0.82);
            border: 1px solid rgba(18, 52, 59, 0.08);
            border-radius: 20px;
            padding: 1rem 1.1rem 1.15rem 1.1rem;
            box-shadow: 0 14px 36px rgba(36, 53, 62, 0.08);
            margin-bottom: 1rem;
        }

        .summary-card {
            background: linear-gradient(135deg, rgba(255,255,255,0.88) 0%, rgba(244,248,249,0.95) 100%);
            border-left: 6px solid #d97a32;
            border-radius: 20px;
            padding: 1rem 1.2rem;
            box-shadow: 0 14px 36px rgba(36, 53, 62, 0.08);
            margin: 0.5rem 0 1rem 0;
        }

        .block-title {
            font-size: 1.05rem;
            font-weight: 800;
            color: #12343b;
            margin: 0 0 0.4rem 0;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


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
        return "нет данных"
    return f"{value * 100:.1f}%"


def format_money(value: float | None) -> str:
    if value is None:
        return "нет данных"
    return f"{value:,.0f} ₽".replace(",", " ")


def display_role_name(role_code: str | None, role_name: str | None = None) -> str:
    if role_code and role_code in ROLE_LABELS:
        return ROLE_LABELS[role_code]
    return role_name or "Все роли"


def display_seniority_list(values: list[str]) -> str:
    if not values:
        return "все уровни"
    return ", ".join(SENIORITY_LABELS.get(value, value) for value in values)


def metric_card(title: str, value: str, subtitle: str) -> str:
    return f"""
    <div class="metric-card">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-subvalue">{subtitle}</div>
    </div>
    """


st.sidebar.markdown("## IT Skills Radar")
st.sidebar.caption("Демо-панель для анализа спроса на навыки в data и product ролях.")

try:
    roles = fetch_roles(API_URL)
except DashboardApiError as exc:
    st.error(str(exc))
    st.stop()

role_options = [{"role_code": "", "role_name": "Все роли"}] + roles
role_labels = [display_role_name(item["role_code"], item["role_name"]) for item in role_options]
selected_role_label = st.sidebar.selectbox("Роль", role_labels, index=0)
selected_role = next(
    item
    for item, label in zip(role_options, role_labels)
    if label == selected_role_label
)

selected_seniority = st.sidebar.multiselect(
    "Уровень",
    options=SENIORITY_OPTIONS,
    default=DEFAULT_SENIORITY,
    format_func=lambda value: SENIORITY_LABELS.get(value, value),
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
selected_skill_label = st.sidebar.selectbox(
    "Навык для динамики",
    options=[label for label, _ in skill_options] if skill_options else ["Нет доступных навыков"],
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
if selected_overview is None and junior_overview:
    selected_overview = max(junior_overview, key=lambda item: item["total_vacancies"])

summary_top_skill = top_skills[0] if top_skills else None
summary_salary = salary_premium[0] if salary_premium else None

st.markdown(
    f"""
    <div class="hero-card">
        <div class="hero-eyebrow">IT Skills Radar</div>
        <div class="hero-title">Русскоязычный обзор рынка навыков<br>для data и product ролей</div>
        <p class="hero-text">
            Панель показывает, какие навыки чаще всего встречаются в вакансиях,
            как меняется их спрос по времени и какие навыки связаны с более высокой зарплатой.
            Все метрики считаются заранее в PostgreSQL, а API и UI только фильтруют и показывают готовые агрегаты.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="summary-card">
        <div class="block-title">Текущий срез</div>
        <div>
            <strong>Роль:</strong> {display_role_name(selected_role_code, selected_role.get('role_name'))}
            &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>Уровень:</strong> {display_seniority_list(list(selected_seniority_tuple))}
            &nbsp;&nbsp;|&nbsp;&nbsp;
            <strong>API:</strong> {API_URL}
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

metric_col_1, metric_col_2, metric_col_3 = st.columns(3)
with metric_col_1:
    st.markdown(
        metric_card(
            "Главный навык",
            summary_top_skill["skill_name"] if summary_top_skill else "Нет данных",
            (
                f"Доля вакансий: {format_share(summary_top_skill['vacancy_share'])}"
                if summary_top_skill
                else "По текущему фильтру данных недостаточно"
            ),
        ),
        unsafe_allow_html=True,
    )
with metric_col_2:
    st.markdown(
        metric_card(
            "Сильнейший salary signal",
            summary_salary["skill_name"] if summary_salary else "Нет данных",
            (
                f"Премия к медиане: {format_money(summary_salary['salary_premium_abs'])}"
                if summary_salary
                else "Недостаточно сопоставимых зарплат"
            ),
        ),
        unsafe_allow_html=True,
    )
with metric_col_3:
    st.markdown(
        metric_card(
            "Медианная зарплата",
            format_money(selected_overview["median_salary_mid"]) if selected_overview else "Нет данных",
            (
                f"Покрытие зарплатой: {format_share(selected_overview['salary_coverage'])}"
                if selected_overview
                else "Нет junior/intern среза"
            ),
        ),
        unsafe_allow_html=True,
    )

if summary_top_skill or summary_salary:
    st.markdown("### Краткий вывод")
    summary_parts: list[str] = []
    if summary_top_skill:
        summary_parts.append(
            f"Для текущего фильтра навык **{summary_top_skill['skill_name']}** встречается чаще всего "
            f"и присутствует в **{format_share(summary_top_skill['vacancy_share'])}** вакансий."
        )
    if summary_salary:
        summary_parts.append(
            f"Наиболее заметная связь с зарплатой сейчас у навыка **{summary_salary['skill_name']}**: "
            f"разница медианной зарплаты составляет около **{format_money(summary_salary['salary_premium_abs'])}**."
        )
    st.info(" ".join(summary_parts))
else:
    st.warning("По текущему фильтру нет достаточного объема аналитических данных.")

left_col, right_col = st.columns([1.25, 1])

with left_col:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Топ навыков")
    if top_skills:
        top_skills_df = pd.DataFrame(top_skills)
        chart_df = (
            top_skills_df[["skill_name", "vacancy_share"]]
            .sort_values("vacancy_share", ascending=True)
            .set_index("skill_name")
        )
        st.bar_chart(chart_df, height=320)

        top_skills_table = top_skills_df[
            ["skill_rank", "skill_name", "vacancy_count", "vacancy_share", "seniority_level"]
        ].rename(
            columns={
                "skill_rank": "Место",
                "skill_name": "Навык",
                "vacancy_count": "Вакансий",
                "vacancy_share": "Доля",
                "seniority_level": "Уровень",
            }
        )
        top_skills_table["Доля"] = top_skills_table["Доля"].map(format_share)
        top_skills_table["Уровень"] = top_skills_table["Уровень"].map(
            lambda value: SENIORITY_LABELS.get(value, value)
        )
        st.dataframe(top_skills_table, use_container_width=True, hide_index=True)
    else:
        st.info("Для выбранного среза нет данных по топу навыков.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Динамика навыка по времени")
    if skill_trends:
        trend_df = pd.DataFrame(skill_trends)
        trend_chart_df = trend_df[["month_start", "vacancy_share"]].copy()
        trend_chart_df["month_start"] = pd.to_datetime(trend_chart_df["month_start"])
        trend_chart_df = trend_chart_df.sort_values("month_start").set_index("month_start")
        st.area_chart(trend_chart_df, height=320)

        trend_table = trend_df[["month_start", "skill_name", "vacancy_count", "vacancy_share"]].rename(
            columns={
                "month_start": "Месяц",
                "skill_name": "Навык",
                "vacancy_count": "Вакансий",
                "vacancy_share": "Доля",
            }
        )
        trend_table["Доля"] = trend_table["Доля"].map(format_share)
        st.dataframe(trend_table, use_container_width=True, hide_index=True)
    else:
        st.info("Нет данных по динамике выбранного навыка.")
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Премия к зарплате")
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
                "skill_name": "Навык",
                "vacancies_with_skill": "С навыком",
                "vacancies_without_skill": "Без навыка",
                "median_salary_with_skill": "Медиана с навыком",
                "median_salary_without_skill": "Медиана без навыка",
                "salary_premium_abs": "Премия, ₽",
                "salary_premium_pct": "Премия, %",
            }
        )
        for column_name in ["Медиана с навыком", "Медиана без навыка", "Премия, ₽"]:
            salary_df[column_name] = salary_df[column_name].map(format_money)
        salary_df["Премия, %"] = salary_df["Премия, %"].map(format_share)
        st.dataframe(salary_df, use_container_width=True, hide_index=True)
    else:
        st.info("Недостаточно данных, чтобы сравнить зарплаты с навыком и без него.")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("Срез по junior и intern")
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
                "role_name": "Роль",
                "seniority_level": "Уровень",
                "total_vacancies": "Вакансий",
                "salary_coverage": "Покрытие зарплатой",
                "median_salary_mid": "Медианная зарплата",
            }
        )
        overview_df["Роль"] = pd.DataFrame(junior_overview).apply(
            lambda row: display_role_name(row["role_code"], row["role_name"]),
            axis=1,
        )
        overview_df["Уровень"] = overview_df["Уровень"].map(lambda value: SENIORITY_LABELS.get(value, value))
        overview_df["Покрытие зарплатой"] = overview_df["Покрытие зарплатой"].map(format_share)
        overview_df["Медианная зарплата"] = overview_df["Медианная зарплата"].map(format_money)
        st.dataframe(overview_df, use_container_width=True, hide_index=True)
    else:
        st.info("Данных по junior и intern ролям пока нет.")
    st.markdown("</div>", unsafe_allow_html=True)

with st.expander("Как устроен этот экран"):
    st.markdown(
        """
        - PostgreSQL заранее считает аналитические витрины: топ навыков, тренды и salary premium.
        - FastAPI отдает уже готовые агрегаты и применяет фильтры по роли и уровню.
        - Streamlit только запрашивает данные из API и собирает их в интерфейс.
        """
    )
    st.code(API_URL)
