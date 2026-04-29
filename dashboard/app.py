from __future__ import annotations

import os
from typing import Any

import pandas as pd
import streamlit as st

from dashboard.api_client import ApiResult
from dashboard.api_client import DashboardApiClient
from dashboard.charts import role_skill_heatmap
from dashboard.charts import salary_chart
from dashboard.charts import top_skills_chart
from dashboard.charts import trends_chart
from dashboard.components import command_bar
from dashboard.components import demo_checklist
from dashboard.components import insight_card
from dashboard.components import interpretation_panel
from dashboard.components import ranked_skill_tiles
from dashboard.components import render_html
from dashboard.components import role_profile_card
from dashboard.components import skill_chip_cloud
from dashboard.components import status_block
from dashboard.components import troubleshooting_panel
from dashboard.demo_checks import DemoCheck
from dashboard.demo_checks import analytics_views_check_from_results
from dashboard.demo_checks import database_check_from_results
from dashboard.demo_checks import normalize_demo_check
from dashboard.demo_checks import sample_data_check_from_results
from dashboard.formatters import DEFAULT_SENIORITY
from dashboard.formatters import SENIORITY_OPTIONS
from dashboard.formatters import display_role_name
from dashboard.formatters import display_seniority
from dashboard.formatters import display_seniority_list
from dashboard.formatters import format_int
from dashboard.formatters import format_money
from dashboard.formatters import format_share
from dashboard.styles import APP_CSS


st.set_page_config(
    page_title="IT Skills Radar",
    page_icon="◎",
    layout="wide",
)

API_URL = os.getenv("API_URL", "http://localhost:8000")
ALL_PERIODS_LABEL = "Все доступные месяцы"


def reset_filters() -> None:
    st.session_state["role_filter"] = "Все роли"
    st.session_state["level_filter"] = DEFAULT_SENIORITY
    st.session_state["skill_filter"] = []
    st.session_state["period_filter"] = ALL_PERIODS_LABEL


def _params(
    role_code: str | None = None,
    seniority_levels: list[str] | None = None,
    rank_limit: int | None = None,
    skill_slug: str | None = None,
) -> dict[str, Any]:
    params: dict[str, Any] = {}
    if role_code:
        params["role_code"] = role_code
    if seniority_levels:
        params["seniority_levels"] = seniority_levels
    if rank_limit is not None:
        params["rank_limit"] = rank_limit
    if skill_slug:
        params["skill_slug"] = skill_slug
    return params


def request_trends_for_skills(
    client: DashboardApiClient,
    role_code: str | None,
    seniority_levels: list[str],
    skill_slugs: list[str],
) -> ApiResult:
    if not skill_slugs:
        return client.request_list(
            "/skills/trends",
            params=_params(role_code, seniority_levels),
        )

    rows: list[dict[str, Any]] = []
    first_error: ApiResult | None = None
    for slug in skill_slugs:
        result = client.request_list(
            "/skills/trends",
            params=_params(role_code, seniority_levels, skill_slug=slug),
        )
        if result.ok and isinstance(result.data, list):
            rows.extend(result.data)
        elif first_error is None:
            first_error = result

    if first_error and not rows:
        return first_error
    return ApiResult(
        endpoint="/skills/trends",
        ok=True,
        status_code=200,
        data=rows,
        message="OK",
    )


def to_dataframe(result: ApiResult) -> pd.DataFrame:
    if result.ok and isinstance(result.data, list):
        return pd.DataFrame(result.data)
    return pd.DataFrame()


def build_role_options(roles_result: ApiResult) -> list[dict[str, str]]:
    roles = roles_result.data if roles_result.ok and isinstance(roles_result.data, list) else []
    return [{"role_code": "", "role_name": "Все роли"}] + roles


def selected_role_code(role_options: list[dict[str, str]], label: str) -> str | None:
    for item in role_options:
        if display_role_name(item.get("role_code"), item.get("role_name")) == label:
            return item.get("role_code") or None
    return None


def skill_options_from_top(top_df: pd.DataFrame) -> list[tuple[str, str]]:
    if top_df.empty:
        return []
    pairs = top_df[["skill_name", "skill_slug"]].drop_duplicates()
    return sorted(
        [(row.skill_name, row.skill_slug) for row in pairs.itertuples()],
        key=lambda item: item[0].lower(),
    )


def periods_from_trends(trend_df: pd.DataFrame) -> list[str]:
    if trend_df.empty or "month_start" not in trend_df:
        return [ALL_PERIODS_LABEL]
    months = (
        pd.to_datetime(trend_df["month_start"])
        .dt.strftime("%Y-%m")
        .dropna()
        .drop_duplicates()
        .sort_values()
        .tolist()
    )
    return [ALL_PERIODS_LABEL] + months


def apply_period_filter(df: pd.DataFrame, period: str) -> pd.DataFrame:
    if df.empty or period == ALL_PERIODS_LABEL or "month_start" not in df:
        return df
    filtered = df.copy()
    filtered["_period"] = pd.to_datetime(filtered["month_start"]).dt.strftime("%Y-%m")
    return filtered[filtered["_period"] == period].drop(columns=["_period"])


def prepare_top_skills_table(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    table = df[
        [
            "skill_rank",
            "skill_name",
            "role_name",
            "seniority_level",
            "vacancy_count",
            "vacancy_share",
        ]
    ].copy()
    table = table.rename(
        columns={
            "skill_rank": "Место",
            "skill_name": "Навык",
            "role_name": "Роль",
            "seniority_level": "Уровень",
            "vacancy_count": "Вакансий",
            "vacancy_share": "Доля вакансий",
        }
    )
    table["Уровень"] = table["Уровень"].map(display_seniority)
    table["Доля вакансий"] = table["Доля вакансий"].map(format_share)
    return table


def prepare_salary_table(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    table = df[
        [
            "skill_name",
            "role_name",
            "seniority_level",
            "vacancies_with_skill",
            "vacancies_without_skill",
            "median_salary_with_skill",
            "median_salary_without_skill",
            "salary_premium_abs",
            "salary_premium_pct",
        ]
    ].copy()
    table = table.rename(
        columns={
            "skill_name": "Навык",
            "role_name": "Роль",
            "seniority_level": "Уровень",
            "vacancies_with_skill": "С навыком",
            "vacancies_without_skill": "Без навыка",
            "median_salary_with_skill": "Медиана с навыком",
            "median_salary_without_skill": "Медиана без навыка",
            "salary_premium_abs": "Сигнал, ₽",
            "salary_premium_pct": "Сигнал, %",
        }
    )
    table["Уровень"] = table["Уровень"].map(display_seniority)
    for column in ["Медиана с навыком", "Медиана без навыка", "Сигнал, ₽"]:
        table[column] = table[column].map(format_money)
    table["Сигнал, %"] = table["Сигнал, %"].map(format_share)
    return table


def prepare_junior_table(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    table = df[
        [
            "role_name",
            "seniority_level",
            "total_vacancies",
            "salary_vacancies",
            "salary_coverage",
            "median_salary_mid",
        ]
    ].copy()
    table = table.rename(
        columns={
            "role_name": "Роль",
            "seniority_level": "Уровень",
            "total_vacancies": "Вакансий",
            "salary_vacancies": "С зарплатой",
            "salary_coverage": "Покрытие зарплатой",
            "median_salary_mid": "Медианная зарплата",
        }
    )
    table["Уровень"] = table["Уровень"].map(display_seniority)
    table["Покрытие зарплатой"] = table["Покрытие зарплатой"].map(format_share)
    table["Медианная зарплата"] = table["Медианная зарплата"].map(format_money)
    return table


def build_demo_checks(results: dict[str, ApiResult]) -> list[DemoCheck]:
    health = results["health"]
    health_ok = (
        health.ok
        and isinstance(health.data, dict)
        and health.data.get("status") == "ok"
    )
    checks = [
        DemoCheck(
            name="API",
            endpoint="/health",
            status="success" if health_ok else "error",
            message="УСПЕХ: API доступен" if health_ok else "ОШИБКА: API недоступен",
        ),
        normalize_demo_check(
            "Роли",
            results["roles"],
            "УСПЕХ: роли загружены",
            "ПРЕДУПРЕЖДЕНИЕ: список ролей пуст",
        ),
        normalize_demo_check(
            "Топ навыков",
            results["top"],
            "УСПЕХ: топ навыков загружен",
            "ПРЕДУПРЕЖДЕНИЕ: данных для выбранного фильтра нет",
        ),
        normalize_demo_check(
            "Динамика навыков",
            results["trends"],
            "УСПЕХ: динамика навыков загружена",
            "ПРЕДУПРЕЖДЕНИЕ: данных для выбранного фильтра нет",
        ),
        normalize_demo_check(
            "Зарплатный сигнал",
            results["salary"],
            "УСПЕХ: зарплатный сигнал загружен",
            "ПРЕДУПРЕЖДЕНИЕ: недостаточно данных по зарплатам",
        ),
        normalize_demo_check(
            "Junior / Intern",
            results["junior"],
            "УСПЕХ: junior/intern обзор загружен",
            "ПРЕДУПРЕЖДЕНИЕ: junior/intern данных пока нет",
        ),
    ]
    api_results = list(results.values())
    checks.append(database_check_from_results(api_results))
    checks.append(analytics_views_check_from_results(api_results))
    checks.append(sample_data_check_from_results(api_results))
    return checks


def render_api_warning(result: ApiResult | None) -> None:
    message = "API недоступен."
    if result is not None and result.status_code == 500:
        message = "Маршрут /roles вернул 500. Запустите prepare_demo."
    elif result is not None and result.message:
        message = result.message
    render_html(troubleshooting_panel(message))


def render_filter_dock(
    client: DashboardApiClient,
    roles_result: ApiResult,
) -> tuple[str | None, list[str], list[str], str]:
    role_options = build_role_options(roles_result)
    role_labels = [
        display_role_name(item.get("role_code"), item.get("role_name"))
        for item in role_options
    ]
    if "role_filter" not in st.session_state:
        st.session_state["role_filter"] = role_labels[0]
    if "level_filter" not in st.session_state:
        st.session_state["level_filter"] = DEFAULT_SENIORITY
    if "period_filter" not in st.session_state:
        st.session_state["period_filter"] = ALL_PERIODS_LABEL

    with st.container(border=True):
        render_html('<div class="dock-native-title">Панель радара</div>')
        col_role, col_level, col_skill, col_period, col_reset = st.columns(
            [1.15, 1.2, 1.45, 1.0, 0.75],
        )
        with col_role:
            role_label = st.selectbox(
                "Роль",
                options=role_labels,
                key="role_filter",
            )
        with col_level:
            levels = st.multiselect(
                "Уровень",
                options=SENIORITY_OPTIONS,
                key="level_filter",
                format_func=display_seniority,
            )

        role_code = selected_role_code(role_options, role_label)
        preliminary_top = client.request_list(
            "/skills/top",
            params=_params(role_code, levels, rank_limit=15),
        )
        preliminary_top_df = to_dataframe(preliminary_top)
        skill_options = skill_options_from_top(preliminary_top_df)
        skill_labels = [label for label, _ in skill_options]
        default_skills = skill_labels[:3]

        if "skill_filter" not in st.session_state:
            st.session_state["skill_filter"] = default_skills
        st.session_state["skill_filter"] = [
            item
            for item in st.session_state["skill_filter"]
            if item in skill_labels
        ]

        with col_skill:
            selected_skill_labels = st.multiselect(
                "Навыки",
                options=skill_labels,
                default=st.session_state["skill_filter"],
                key="skill_filter",
                disabled=not skill_labels,
            )

        selected_slugs = [
            slug
            for label, slug in skill_options
            if label in selected_skill_labels
        ]
        preliminary_trends = request_trends_for_skills(
            client,
            role_code,
            levels,
            selected_slugs,
        )
        period_options = periods_from_trends(to_dataframe(preliminary_trends))
        if st.session_state["period_filter"] not in period_options:
            st.session_state["period_filter"] = ALL_PERIODS_LABEL

        with col_period:
            period = st.selectbox(
                "Период",
                options=period_options,
                key="period_filter",
            )
        with col_reset:
            st.button(
                "Сбросить",
                on_click=reset_filters,
                use_container_width=True,
            )
    return role_code, levels, selected_slugs, period


def render_market_tab(
    roles_result: ApiResult,
    top_df: pd.DataFrame,
    trend_df: pd.DataFrame,
    salary_df: pd.DataFrame,
    role_code: str | None,
    levels: list[str],
) -> None:
    st.subheader("Карта рынка")
    left, center, right = st.columns([1.0, 1.55, 1.0])
    skills_count = top_df["skill_slug"].nunique() if not top_df.empty else 0
    top_skill = top_df.iloc[0]["skill_name"] if not top_df.empty else None
    salary_signal = "нет данных"
    if not salary_df.empty:
        max_signal = salary_df["salary_premium_abs"].dropna().max()
        salary_signal = format_money(max_signal) if pd.notna(max_signal) else "нет данных"

    with left:
        render_html(
            role_profile_card(
                display_role_name(role_code),
                display_seniority_list(levels),
                skills_count,
                len(top_df),
            ),
        )
        render_html(
            insight_card(
                "Роли в справочнике",
                format_int(roles_result.rows_count if roles_result.ok else 0),
                "Данные берутся из маршрута /roles",
            ),
        )
    with center:
        if top_df.empty:
            render_html(status_block("warning", "Для выбранного среза нет навыков."))
        else:
            render_html(ranked_skill_tiles(top_df, limit=6))
            render_html(skill_chip_cloud(top_df, limit=12))
    with right:
        render_html(interpretation_panel(top_skill, salary_signal))
        render_html(
            insight_card(
                "Точек динамики",
                format_int(len(trend_df)),
                "Исторические месячные наблюдения, не прогноз",
            ),
        )

    with st.expander("Как читать dashboard", expanded=False):
        st.markdown(
            """
            - `Доля вакансий` показывает, в какой части выбранного среза встречается навык.
            - `Матрица навыков` помогает сравнить роли и уровни.
            - `Динамика спроса` показывает упоминания по месяцам, а не прогноз.
            - `Зарплатный сигнал` не доказывает причинность.
            """
        )


def render_matrix_tab(matrix_df: pd.DataFrame) -> None:
    st.subheader("Матрица навыков")
    st.caption(
        "Тепловая карта показывает, где навыки чаще встречаются по ролям "
        "и уровням. Чем насыщеннее цвет, тем выше доля вакансий."
    )
    if matrix_df.empty:
        render_html(status_block("warning", "Матрица пуста для выбранного фильтра."))
        return
    st.altair_chart(role_skill_heatmap(matrix_df), use_container_width=True)
    table = prepare_top_skills_table(matrix_df)
    st.dataframe(table, use_container_width=True, hide_index=True)


def render_trends_tab(trend_result: ApiResult, trend_df: pd.DataFrame) -> None:
    st.subheader("Динамика спроса")
    st.caption("Это динамика упоминаний навыка по месяцам, а не прогноз.")
    if not trend_result.ok:
        render_api_warning(trend_result)
        return
    if trend_df.empty:
        render_html(status_block("warning", "По выбранным навыкам нет динамики."))
        return
    st.altair_chart(trends_chart(trend_df), use_container_width=True)
    table = trend_df[
        [
            "month_start",
            "skill_name",
            "role_name",
            "seniority_level",
            "vacancy_count",
            "vacancy_share",
        ]
    ].copy()
    table = table.rename(
        columns={
            "month_start": "Месяц",
            "skill_name": "Навык",
            "role_name": "Роль",
            "seniority_level": "Уровень",
            "vacancy_count": "Вакансий",
            "vacancy_share": "Доля вакансий",
        }
    )
    table["Уровень"] = table["Уровень"].map(display_seniority)
    table["Доля вакансий"] = table["Доля вакансий"].map(format_share)
    st.dataframe(table, use_container_width=True, hide_index=True)


def render_salary_tab(salary_result: ApiResult, salary_df: pd.DataFrame) -> None:
    st.subheader("Зарплатный сигнал")
    st.caption(
        "Salary premium показывает аналитическую связь, а не причинность."
    )
    if not salary_result.ok:
        render_api_warning(salary_result)
        return
    if salary_df.empty:
        render_html(status_block("warning", "Недостаточно зарплатных данных."))
        return

    positive_df = salary_df.dropna(subset=["salary_premium_abs"])
    positive_df = positive_df.sort_values("salary_premium_abs", ascending=False)
    if not positive_df.empty:
        leader = positive_df.iloc[0]
        cols = st.columns(3)
        with cols[0]:
            render_html(
                insight_card(
                    "Самый заметный сигнал",
                    str(leader["skill_name"]),
                    f"Разница медиан: {format_money(leader['salary_premium_abs'])}",
                ),
            )
        with cols[1]:
            render_html(
                insight_card(
                    "Вакансий с навыком",
                    format_int(leader["vacancies_with_skill"]),
                    "Сравнение внутри роли и уровня",
                ),
            )
        with cols[2]:
            render_html(
                insight_card(
                    "Относительный сигнал",
                    format_share(leader["salary_premium_pct"]),
                    "Интерпретировать осторожно",
                ),
            )
        st.altair_chart(salary_chart(positive_df), use_container_width=True)
    st.dataframe(prepare_salary_table(salary_df), use_container_width=True, hide_index=True)


def render_junior_tab(junior_result: ApiResult, junior_df: pd.DataFrame) -> None:
    st.subheader("Junior / Intern")
    st.caption(
        "Раздел показывает entry-level вход: роли, зарплатное покрытие "
        "и базовый стек для первых откликов."
    )
    if not junior_result.ok:
        render_api_warning(junior_result)
        return
    if junior_df.empty:
        render_html(status_block("warning", "Junior/intern данных пока нет."))
        return

    top_row = junior_df.sort_values("total_vacancies", ascending=False).iloc[0]
    render_html(
        status_block(
            "success",
            (
                "На junior/intern позициях чаще всего встречается роль "
                f"<strong>{top_row['role_name']}</strong>: "
                f"{format_int(top_row['total_vacancies'])} вакансий."
            ),
        ),
    )
    render_html(
        '<div class="chip-cloud">'
        '<span class="skill-chip">SQL</span>'
        '<span class="skill-chip">Python</span>'
        '<span class="skill-chip">pandas</span>'
        '<span class="skill-chip">A/B testing</span>'
        '<span class="skill-chip">BI / dashboards</span>'
        "</div>",
    )
    st.dataframe(prepare_junior_table(junior_df), use_container_width=True, hide_index=True)


def render_checks_tab(checks: list[DemoCheck]) -> None:
    st.subheader("Проверка демо")
    st.caption("Чеклист показывает, готов ли проект к демонстрации.")
    render_html(demo_checklist(checks))


render_html(APP_CSS)
client = DashboardApiClient(API_URL)
health_result = client.request_json("/health")
roles_result = client.request_list("/roles")
junior_status_result = client.request_list("/overview/junior")

render_html(command_bar(health_result.ok, junior_status_result.rows_count > 0))
_, swagger_col, refresh_col = st.columns([6.0, 1.0, 1.0])
with swagger_col:
    st.link_button("Swagger", "http://localhost:8000/docs", use_container_width=True)
with refresh_col:
    if st.button("Обновить", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

role_code, levels, selected_skills, period = render_filter_dock(
    client,
    roles_result,
)

top_result = client.request_list(
    "/skills/top",
    params=_params(role_code, levels, rank_limit=15),
)
matrix_result = client.request_list(
    "/skills/top",
    params=_params(None, levels, rank_limit=15),
)
trend_result = request_trends_for_skills(client, role_code, levels, selected_skills)
salary_result = client.request_list(
    "/salary/premium",
    params=_params(
        role_code,
        levels,
        skill_slug=selected_skills[0] if selected_skills else None,
    ),
)
junior_result = client.request_list("/overview/junior")

top_df = to_dataframe(top_result)
matrix_df = to_dataframe(matrix_result)
trend_df = apply_period_filter(to_dataframe(trend_result), period)
salary_df = to_dataframe(salary_result)
junior_df = to_dataframe(junior_result)

if not health_result.ok or not roles_result.ok:
    render_api_warning(roles_result if not roles_result.ok else health_result)

tabs = st.tabs(
    [
        "Карта рынка",
        "Матрица навыков",
        "Динамика спроса",
        "Зарплатный сигнал",
        "Junior / Intern",
        "Проверка демо",
    ],
)

with tabs[0]:
    render_market_tab(
        roles_result,
        top_df,
        trend_df,
        salary_df,
        role_code,
        levels,
    )
    if not top_df.empty:
        st.altair_chart(top_skills_chart(top_df), use_container_width=True)

with tabs[1]:
    render_matrix_tab(matrix_df)

with tabs[2]:
    render_trends_tab(trend_result, trend_df)

with tabs[3]:
    render_salary_tab(salary_result, salary_df)

with tabs[4]:
    render_junior_tab(junior_result, junior_df)

with tabs[5]:
    render_checks_tab(
        build_demo_checks(
            {
                "health": health_result,
                "roles": roles_result,
                "top": top_result,
                "trends": trend_result,
                "salary": salary_result,
                "junior": junior_result,
            },
        ),
    )
