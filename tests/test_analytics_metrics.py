from app.services.analytics import calculate_salary_premium_pct
from app.services.analytics import calculate_share


def test_calculate_share_returns_ratio() -> None:
    assert calculate_share(3, 10) == 0.3


def test_calculate_share_returns_none_for_zero_denominator() -> None:
    assert calculate_share(3, 0) is None


def test_calculate_salary_premium_pct_returns_practical_ratio() -> None:
    assert calculate_salary_premium_pct(180000, 150000) == 0.2


def test_calculate_salary_premium_pct_returns_none_for_missing_baseline() -> None:
    assert calculate_salary_premium_pct(180000, 0) is None
    assert calculate_salary_premium_pct(None, 150000) is None
