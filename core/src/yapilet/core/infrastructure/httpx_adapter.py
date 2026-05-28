from __future__ import annotations

from typing import Any

import httpx

from yapilet.core.models.api_request import ApiRequest
from yapilet.core.ports.http_port import HttpPort, RawResponse


class HttpxAdapter(HttpPort):
    """Real HTTP transport backed by httpx."""

    def __init__(self, timeout: float = 30.0) -> None:
        self._timeout = timeout

    def send(self, request: ApiRequest) -> RawResponse:
        with httpx.Client(timeout=self._timeout) as client:
            response = client.request(
                method=request.method,
                url=request.url,
                headers=request.headers or None,
                json=request.body or None,
            )
        body: Any
        try:
            body = response.json()
        except ValueError:
            body = response.text
        return RawResponse(
            status_code=response.status_code,
            body=body,
            headers=dict(response.headers),
        )
