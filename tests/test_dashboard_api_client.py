import httpx
import pytest

from dashboard.api_client import DashboardApiClient
from dashboard.api_client import DashboardApiError


class DummyResponse:
    def __init__(self, payload: object, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "error",
                request=httpx.Request("GET", "http://test"),
                response=httpx.Response(self.status_code),
            )

    def json(self) -> object:
        return self._payload


def test_dashboard_api_client_returns_list_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(url: str, params: dict | None = None, timeout: float = 20.0) -> DummyResponse:
        return DummyResponse([{"role_code": "data_scientist"}])

    monkeypatch.setattr(httpx, "get", fake_get)

    client = DashboardApiClient("http://localhost:8000")

    assert client.get_roles()[0]["role_code"] == "data_scientist"


def test_dashboard_api_client_raises_readable_error_on_http_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_get(url: str, params: dict | None = None, timeout: float = 20.0) -> DummyResponse:
        return DummyResponse([], status_code=500)

    monkeypatch.setattr(httpx, "get", fake_get)

    client = DashboardApiClient("http://localhost:8000")

    with pytest.raises(DashboardApiError) as exc_info:
        client.get_roles()

    assert "Не удалось загрузить данные" in str(exc_info.value)


def test_dashboard_api_client_raises_error_for_unexpected_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_get(url: str, params: dict | None = None, timeout: float = 20.0) -> DummyResponse:
        return DummyResponse({"unexpected": True})

    monkeypatch.setattr(httpx, "get", fake_get)

    client = DashboardApiClient("http://localhost:8000")

    with pytest.raises(DashboardApiError) as exc_info:
        client.get_roles()

    assert "неожиданный формат" in str(exc_info.value).lower()
