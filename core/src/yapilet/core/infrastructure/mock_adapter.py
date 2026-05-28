from __future__ import annotations

from typing import Any

from yapilet.core.models.api_request import ApiRequest
from yapilet.core.ports.http_port import HttpPort, RawResponse


class MockAdapter(HttpPort):
    """Offline mock adapter. Echoes the request back as the response body."""

    def __init__(self, fixed_response: dict[str, Any] | None = None) -> None:
        self._fixed = fixed_response

    def send(self, request: ApiRequest) -> RawResponse:
        if self._fixed is not None:
            return RawResponse(status_code=200, body=self._fixed)
        echoed: dict[str, Any] = {
            "echo": {
                "method": request.method,
                "url": request.url,
                "headers": dict(request.headers),
                "body": dict(request.body),
            }
        }
        return RawResponse(status_code=200, body=echoed)
