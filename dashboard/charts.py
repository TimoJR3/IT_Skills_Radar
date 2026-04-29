from __future__ import annotations

import altair as alt
import pandas as pd


def top_skills_chart(df: pd.DataFrame) -> alt.Chart:
    chart_df = df.copy()
    chart_df["Доля вакансий"] = chart_df["vacancy_share"].fillna(0) * 100
    return (
        alt.Chart(chart_df)
        .mark_bar(color="#6366f1", cornerRadiusEnd=4)
        .encode(
            x=alt.X("Доля вакансий:Q", title="Доля вакансий, %"),
            y=alt.Y("skill_name:N", title="Навык", sort="-x"),
            tooltip=[
                alt.Tooltip("skill_name:N", title="Навык"),
                alt.Tooltip("vacancy_count:Q", title="Вакансий"),
                alt.Tooltip("Доля вакансий:Q", title="Доля, %", format=".1f"),
            ],
        )
        .properties(height=max(260, min(520, len(chart_df) * 34)))
        .configure_view(stroke=None)
    )


def trends_chart(df: pd.DataFrame) -> alt.Chart:
    chart_df = df.copy()
    chart_df["month_start"] = pd.to_datetime(chart_df["month_start"])
    chart_df["Доля вакансий"] = chart_df["vacancy_share"].fillna(0) * 100
    return (
        alt.Chart(chart_df)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X("month_start:T", title="Месяц"),
            y=alt.Y("Доля вакансий:Q", title="Доля вакансий, %"),
            color=alt.Color(
                "skill_name:N",
                title="Навык",
                scale=alt.Scale(range=["#6366f1", "#06b6d4", "#f59e0b"]),
            ),
            tooltip=[
                alt.Tooltip("month_start:T", title="Месяц", format="%Y-%m"),
                alt.Tooltip("skill_name:N", title="Навык"),
                alt.Tooltip("vacancy_count:Q", title="Вакансий"),
                alt.Tooltip("Доля вакансий:Q", title="Доля, %", format=".1f"),
            ],
        )
        .properties(height=340)
        .configure_view(stroke=None)
    )


def salary_chart(df: pd.DataFrame) -> alt.Chart:
    chart_df = df.dropna(subset=["salary_premium_abs"]).copy()
    chart_df = chart_df.sort_values("salary_premium_abs", ascending=False).head(12)
    return (
        alt.Chart(chart_df)
        .mark_bar(color="#f59e0b", cornerRadiusEnd=4)
        .encode(
            x=alt.X("salary_premium_abs:Q", title="Зарплатный сигнал, ₽"),
            y=alt.Y("skill_name:N", title="Навык", sort="-x"),
            tooltip=[
                alt.Tooltip("skill_name:N", title="Навык"),
                alt.Tooltip("salary_premium_abs:Q", title="Сигнал, ₽", format=",.0f"),
                alt.Tooltip("salary_premium_pct:Q", title="Сигнал, %", format=".1%"),
            ],
        )
        .properties(height=max(260, min(480, len(chart_df) * 34)))
        .configure_view(stroke=None)
    )


def role_skill_heatmap(df: pd.DataFrame) -> alt.Chart:
    chart_df = df.copy()
    chart_df["Доля вакансий"] = chart_df["vacancy_share"].fillna(0) * 100
    return (
        alt.Chart(chart_df)
        .mark_rect(cornerRadius=2)
        .encode(
            x=alt.X("role_name:N", title="Роль"),
            y=alt.Y("skill_name:N", title="Навык", sort="-x"),
            color=alt.Color(
                "Доля вакансий:Q",
                title="Доля, %",
                scale=alt.Scale(scheme="purples"),
            ),
            tooltip=[
                alt.Tooltip("role_name:N", title="Роль"),
                alt.Tooltip("skill_name:N", title="Навык"),
                alt.Tooltip("seniority_level:N", title="Уровень"),
                alt.Tooltip("vacancy_count:Q", title="Вакансий"),
                alt.Tooltip("Доля вакансий:Q", title="Доля, %", format=".1f"),
            ],
        )
        .properties(height=max(320, min(620, df["skill_name"].nunique() * 26)))
        .configure_view(stroke=None)
    )
