from __future__ import annotations

from pathlib import Path
from typing import Any

from yapilet.core.models.api_request import ApiRequest
from yapilet.core.models.result import Result
from yapilet.core.ports.http_port import HttpPort
from yapilet.core.services.api_client import ApiClient
from yapilet.core.services.config_loader import ConfigLoader
from yapilet.core.services.placeholder import PlaceholderResolver


class ExecuteMessagesUseCase:
    """Load messages config -> expand placeholders -> send -> extract."""

    def __init__(
        self,
        *,
        http_port: HttpPort,
        config_loader: ConfigLoader,
        resolver: PlaceholderResolver | None = None,
    ) -> None:
        self._client = ApiClient(http_port)
        self._loader = config_loader
        self._resolver = resolver or PlaceholderResolver()

    def run(
        self,
        config_path: str | Path,
        *,
        user_inputs: list[str] | None = None,
        api_key: str | None = None,
    ) -> Result:
        template = self._loader.load_messages(Path(config_path))

        resolved_messages: list[dict[str, Any]] = self._resolver.resolve_in_object(
            list(template.messages),
            user_inputs=user_inputs,
            api_key=api_key,
        )
        resolved_headers: dict[str, str] = self._resolver.resolve_in_object(
            dict(template.headers),
            user_inputs=user_inputs,
            api_key=api_key,
        )

        body: dict[str, Any] = {**template.body_extra, "messages": resolved_messages}

        request = ApiRequest(
            title=template.title,
            method="POST",
            url=self._resolver.resolve(template.url, user_inputs=user_inputs, api_key=api_key),
            headers=resolved_headers,
            body=body,
            response_path=template.response_path,
            note=template.note,
        )

        return self._client.send(request)
