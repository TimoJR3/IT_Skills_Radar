from __future__ import annotations


SENIORITY_OPTIONS = ["intern", "junior", "middle", "senior", "lead", "unknown"]
DEFAULT_SENIORITY = ["junior", "intern"]

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
    "intern_analyst": "Intern Analyst",
    "other_data_role": "Смежная data/product роль",
}


def format_share(value: float | int | None) -> str:
    if value is None:
        return "нет данных"
    return f"{float(value) * 100:.1f}%"


def format_money(value: float | int | None) -> str:
    if value is None:
        return "нет данных"
    return f"{float(value):,.0f} ₽".replace(",", " ")


def format_int(value: int | float | None) -> str:
    if value is None:
        return "0"
    return f"{int(value):,}".replace(",", " ")


def display_role_name(role_code: str | None, role_name: str | None = None) -> str:
    if role_code and role_code in ROLE_LABELS:
        return ROLE_LABELS[role_code]
    return role_name or "Все роли"


def display_seniority(value: str | None) -> str:
    if value is None:
        return "Не указан"
    return SENIORITY_LABELS.get(value, value)


def display_seniority_list(values: list[str] | tuple[str, ...]) -> str:
    if not values:
        return "все уровни"
    return ", ".join(display_seniority(value) for value in values)
