from __future__ import annotations

from unittest.mock import MagicMock, patch

from yapilet.core.infrastructure.httpx_adapter import HttpxAdapter
from yapilet.core.models.api_request import ApiRequest


def _make_mock_response(
    status_code: int, body: dict | None = None, text: str = ""
) -> MagicMock:
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.headers = {"Content-Type": "application/json"}
    if body is not None:
        mock_response.json.return_value = body
    else:
        mock_response.json.side_effect = ValueError("no JSON")
        mock_response.text = text
    return mock_response


def _make_request() -> ApiRequest:
    return ApiRequest(
        title="test",
        method="GET",
        url="https://example.com",
    )


def test_httpx_adapter_default_timeout() -> None:
    with patch("yapilet.core.infrastructure.httpx_adapter.httpx.Client") as mock_cls:
        mock_ctx = MagicMock()
        mock_ctx.request.return_value = _make_mock_response(200, {"ok": True})
        mock_cls.return_value.__enter__ = MagicMock(return_value=mock_ctx)
        mock_cls.return_value.__exit__ = MagicMock(return_value=False)

        adapter = HttpxAdapter()  # default timeout
        adapter.send(_make_request())

        mock_cls.assert_called_once_with(timeout=30.0)


def test_httpx_adapter_send_json_response() -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"result": "ok"}
    mock_response.headers = {"Content-Type": "application/json"}

    mock_client = MagicMock()
    mock_client.request.return_value = mock_response
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)

    with patch(
        "yapilet.core.infrastructure.httpx_adapter.httpx.Client",
        return_value=mock_client,
    ):
        adapter = HttpxAdapter()
        raw = adapter.send(_make_request())

    assert raw.status_code == 200
    assert raw.body == {"result": "ok"}
    assert raw.headers == {"Content-Type": "application/json"}
    mock_client.request.assert_called_once_with(
        method="GET",
        url="https://example.com",
        headers=None,
        json=None,
    )


def test_httpx_adapter_send_text_response_on_json_decode_error() -> None:
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.side_effect = ValueError("no JSON")
    mock_response.text = "plain text body"
    mock_response.headers = {"Content-Type": "text/plain"}

    mock_client = MagicMock()
    mock_client.request.return_value = mock_response
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)

    with patch(
        "yapilet.core.infrastructure.httpx_adapter.httpx.Client",
        return_value=mock_client,
    ):
        adapter = HttpxAdapter()
        raw = adapter.send(_make_request())

    assert raw.status_code == 200
    assert raw.body == "plain text body"
    assert raw.headers == {"Content-Type": "text/plain"}
