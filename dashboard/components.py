from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from dashboard.demo_checks import DemoCheck
from dashboard.demo_checks import checks_to_rows
from dashboard.demo_checks import status_label
from dashboard.formatters import format_int
from dashboard.formatters import format_share


def render_html(html: str) -> None:
    st.markdown(html, unsafe_allow_html=True)


def pill(text: str, kind: str = "default") -> str:
    css_class = {
        "success": "pill pill-ok",
        "warning": "pill pill-warn",
        "error": "pill pill-error",
    }.get(kind, "pill")
    return f'<span class="{css_class}">{escape(text)}</span>'


def command_bar(api_ok: bool, demo_ready: bool) -> str:
    api_status = pill("API доступен", "success") if api_ok else pill(
        "API недоступен",
        "error",
    )
    demo_status = pill("Демо-данные готовы", "success") if demo_ready else pill(
        "Демо-данные не найдены",
        "warning",
    )
    return f"""
    <div class="command-bar">
        <div>
            <div class="product-title">IT Skills Radar</div>
            <div class="product-subtitle">
                Карта спроса на навыки в data/product вакансиях
            </div>
        </div>
        <div class="bar-actions">
            {api_status}
            {demo_status}
            <span class="pipeline-badge">
                JSON/CSV → PostgreSQL → SQL-витрины → FastAPI → Streamlit
            </span>
        </div>
    </div>
    """


def filter_dock_start() -> str:
    return '<div class="filter-dock"><div class="dock-title">Панель радара</div>'


def filter_dock_end() -> str:
    return "</div>"


def status_block(kind: str, text: str) -> str:
    css_class = {
        "success": "status-ok",
        "warning": "status-warn",
        "error": "status-error",
    }.get(kind, "status-warn")
    return f'<div class="status {css_class}">{text}</div>'


def troubleshooting_panel(message: str) -> str:
    commands = [
        "docker compose ps",
        "docker compose logs api --tail=100",
        "docker compose up --build -d",
        "docker compose exec api python -m app.db.prepare_demo",
    ]
    command_rows = "".join(
        f'<div class="command-item">{escape(command)}</div>'
        for command in commands
    )
    return (
        status_block(
            "error",
            f"{escape(message)} Проверьте, что контейнеры запущены.",
        )
        + '<div class="command-list">'
        + command_rows
        + '<div class="command-item">Swagger: http://localhost:8000/docs</div>'
        + "</div>"
    )


def role_profile_card(
    role_name: str,
    levels: str,
    skills_count: int,
    rows_count: int,
) -> str:
    return f"""
    <div class="soft-panel">
        <div class="role-profile-title">Профиль роли</div>
        <div class="role-profile-value">{escape(role_name)}</div>
        <div class="panel-text">
            Уровни: <strong>{escape(levels)}</strong><br>
            Видимых навыков: <strong>{format_int(skills_count)}</strong><br>
            Строк в текущем срезе: <strong>{format_int(rows_count)}</strong>
        </div>
    </div>
    """


def interpretation_panel(top_skill: str | None, salary_signal: str) -> str:
    if top_skill:
        text = (
            f"В выбранном срезе чаще всего встречается навык "
            f"<strong>{escape(top_skill)}</strong>. "
            "Используйте вкладки, чтобы сравнить спрос, динамику и зарплатный "
            "сигнал без перехода к сырой таблице."
        )
    else:
        text = (
            "Для текущего фильтра данных мало. Проверьте роль, уровень или "
            "подготовьте демо-данные через команду prepare_demo."
        )
    return f"""
    <div class="soft-panel">
        <div class="role-profile-title">Интерпретация</div>
        <div class="panel-text">{text}</div>
        <div class="chip-cloud">
            <span class="skill-chip">Зарплатный сигнал: {escape(salary_signal)}</span>
        </div>
    </div>
    """


def ranked_skill_tiles(df: pd.DataFrame, limit: int = 6) -> str:
    if df.empty:
        return ""
    tiles = []
    for index, row in enumerate(df.head(limit).itertuples(), start=1):
        leader = " ranked-tile-leader" if index == 1 else ""
        tiles.append(
            f'<div class="ranked-tile{leader}">'
            f'<div class="rank-label">#{index}</div>'
            f'<div class="rank-name">{escape(str(row.skill_name))}</div>'
            '<div class="rank-meta">'
            f'{format_int(row.vacancy_count)} вакансий · '
            f'{format_share(row.vacancy_share)} выбранного среза'
            "</div></div>"
        )
    return '<div class="ranked-grid">' + "".join(tiles) + "</div>"


def skill_chip_cloud(df: pd.DataFrame, limit: int = 14) -> str:
    if df.empty:
        return ""
    chips = []
    for row in df.head(limit).itertuples():
        chips.append(
            '<span class="skill-chip">'
            f'{escape(str(row.skill_name))} · {format_share(row.vacancy_share)}'
            "</span>"
        )
    return '<div class="chip-cloud">' + "".join(chips) + "</div>"


def insight_card(title: str, value: str, caption: str) -> str:
    return f"""
    <div class="insight-card">
        <div class="insight-title">{escape(title)}</div>
        <div class="insight-value">{escape(value)}</div>
        <div class="panel-text">{escape(caption)}</div>
    </div>
    """


def demo_checklist(checks: list[DemoCheck]) -> str:
    rows = checks_to_rows(checks)
    html_rows = [
        '<div class="check-row check-head">'
        "<div>Проверка</div><div>Маршрут</div><div>Статус</div>"
        "<div>Сообщение</div><div>Строк</div></div>"
    ]
    for row in rows:
        status = status_label(str(row["Статус"]).lower())
        # rows already contain Russian labels; keep fallback harmless.
        status = row["Статус"] if row["Статус"] in {
            "УСПЕХ",
            "ПРЕДУПРЕЖДЕНИЕ",
            "ОШИБКА",
        } else status
        html_rows.append(
            '<div class="check-row">'
            f"<div>{escape(str(row['Проверка']))}</div>"
            f"<div>{escape(str(row['Маршрут']))}</div>"
            f"<div>{escape(str(status))}</div>"
            f"<div>{escape(str(row['Сообщение']))}</div>"
            f"<div>{escape('' if row['Строк'] is None else str(row['Строк']))}</div>"
            "</div>"
        )
    return "".join(html_rows)
