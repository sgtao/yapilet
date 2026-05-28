from __future__ import annotations

import jmespath

from yapilet.core.models.api_request import ApiRequest
from yapilet.core.models.result import Result
from yapilet.core.ports.http_port import HttpPort


class ApiClient:
    """Executes an ApiRequest via HttpPort and applies response_path extraction."""

    def __init__(self, http_port: HttpPort) -> None:
        self._http = http_port

    def send(self, request: ApiRequest) -> Result:
        try:
            raw = self._http.send(request)
        except Exception as e:  # noqa: BLE001
            return Result(
                status_code=0,
                body=None,
                extracted=None,
                is_success=False,
                error=f"{type(e).__name__}: {e}",
            )

        extracted = None
        if request.response_path:
            try:
                extracted = jmespath.search(request.response_path, raw.body)
            except Exception as e:  # noqa: BLE001
                return Result(
                    status_code=raw.status_code,
                    body=raw.body,
                    extracted=None,
                    is_success=False,
                    error=f"jmespath error: {e}",
                    raw_headers=raw.headers,
                )

        is_success = 200 <= raw.status_code < 300
        return Result(
            status_code=raw.status_code,
            body=raw.body,
            extracted=extracted,
            is_success=is_success,
            raw_headers=raw.headers,
        )
