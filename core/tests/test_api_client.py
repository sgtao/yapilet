from __future__ import annotations

from unittest.mock import patch

from yapilet.core.infrastructure.mock_adapter import MockAdapter
from yapilet.core.models.api_request import ApiRequest
from yapilet.core.ports.http_port import HttpPort, RawResponse
from yapilet.core.services.api_client import ApiClient


def _make_request(response_path: str | None = None) -> ApiRequest:
    return ApiRequest(
        title="test",
        method="GET",
        url="https://example.com",
        response_path=response_path,
    )


class _RaisingHttpPort(HttpPort):
    """HttpPort stub that always raises RuntimeError."""

    def send(self, request: ApiRequest) -> RawResponse:
        raise RuntimeError("connection refused")


def test_api_client_http_send_raises_returns_error_result() -> None:
    client = ApiClient(_RaisingHttpPort())
    result = client.send(_make_request())

    assert result.status_code == 0
    assert result.is_success is False
    assert result.error == "RuntimeError: connection refused"


def test_api_client_jmespath_error_returns_error_result() -> None:
    adapter = MockAdapter(fixed_response={"key": "val"})
    client = ApiClient(adapter)
    request = _make_request(response_path="bad.expr")

    with patch(
        "yapilet.core.services.api_client.jmespath.search",
        side_effect=ValueError("bad expr"),
    ):
        result = client.send(request)

    assert result.is_success is False
    assert result.error is not None
    assert result.error.startswith("jmespath error:")


def test_mock_adapter_fixed_response_is_returned() -> None:
    fixed = {"key": "val"}
    adapter = MockAdapter(fixed_response=fixed)
    raw = adapter.send(_make_request())

    assert raw.body == fixed
