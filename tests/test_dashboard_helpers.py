from dashboard.api_client import ApiResult
from dashboard.components import command_bar
from dashboard.components import ranked_skill_tiles
from dashboard.components import troubleshooting_panel
from dashboard.demo_checks import checks_to_rows
from dashboard.demo_checks import normalize_demo_check
from dashboard.demo_checks import status_label
from dashboard.formatters import display_seniority
from dashboard.formatters import format_money
from dashboard.formatters import format_share


def test_formatters_return_russian_friendly_values() -> None:
    assert format_share(0.125) == "12.5%"
    assert format_money(150000) == "150 000 ₽"
    assert display_seniority("intern") == "Стажер"


def test_status_label_returns_russian_labels() -> None:
    assert status_label("success") == "УСПЕХ"
    assert status_label("warning") == "ПРЕДУПРЕЖДЕНИЕ"
    assert status_label("error") == "ОШИБКА"


def test_normalize_demo_check_marks_empty_data_as_warning() -> None:
    result = ApiResult(
        endpoint="/skills/top",
        ok=True,
        status_code=200,
        data=[],
        message="OK",
    )

    check = normalize_demo_check(
        name="Топ навыков",
        result=result,
        success_message="УСПЕХ: топ навыков загружен",
        empty_message="ПРЕДУПРЕЖДЕНИЕ: данных для выбранного фильтра нет",
    )

    assert check.status == "warning"
    assert check.message.startswith("ПРЕДУПРЕЖДЕНИЕ")


def test_checks_to_rows_uses_russian_statuses() -> None:
    result = ApiResult(
        endpoint="/roles",
        ok=False,
        status_code=500,
        data={"detail": "broken"},
        message="Endpoint /roles вернул 500.",
    )
    check = normalize_demo_check(
        name="Роли",
        result=result,
        success_message="УСПЕХ: роли загружены",
        empty_message="ПРЕДУПРЕЖДЕНИЕ: список ролей пуст",
    )

    rows = checks_to_rows([check])

    assert rows[0]["Статус"] == "ОШИБКА"
    assert rows[0]["Маршрут"] == "/roles"
    assert rows[0]["Сообщение"] == "ОШИБКА: маршрут /roles вернул 500"


def test_command_bar_returns_valid_radar_markup() -> None:
    html = command_bar(api_ok=True, demo_ready=True)

    assert "IT Skills Radar" in html
    assert "API доступен" in html
    assert "<div" in html
    assert html.count("<div") == html.count("</div>")


def test_troubleshooting_panel_contains_demo_command() -> None:
    html = troubleshooting_panel("API недоступен.")

    assert "docker compose ps" in html
    assert "python -m app.db.prepare_demo" in html
    assert html.count("<div") == html.count("</div>")


def test_ranked_skill_tiles_escapes_skill_names() -> None:
    import pandas as pd

    df = pd.DataFrame(
        [
            {
                "skill_name": "<SQL>",
                "vacancy_count": 2,
                "vacancy_share": 0.5,
            }
        ]
    )

    html = ranked_skill_tiles(df)

    assert "&lt;SQL&gt;" in html
    assert "<SQL>" not in html
