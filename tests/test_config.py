from app.core.config import settings


def test_settings_has_app_name() -> None:
    assert settings.app_name == "IT Skills Radar"
