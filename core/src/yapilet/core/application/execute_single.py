from __future__ import annotations

from yapilet.core.models.api_request import ApiRequest
from yapilet.core.models.result import Result
from yapilet.core.ports.http_port import HttpPort
from yapilet.core.services.api_client import ApiClient
from yapilet.core.services.config_loader import ConfigLoader
from yapilet.core.services.placeholder import PlaceholderResolver


class ExecuteSingleUseCase:
    """Orchestrates: load config -> expand placeholders -> send -> extract."""

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
        config_name: str,
        *,
        user_inputs: list[str] | None = None,
        api_key: str | None = None,
        action_results: list[str] | None = None,  # reserved for Phase 1.5
    ) -> Result:
        template = self._loader.load_single(config_name)
        resolved = self._expand(
            template,
            user_inputs=user_inputs,
            api_key=api_key,
            action_results=action_results,
        )
        return self._client.send(resolved)

    def _expand(
        self,
        template: ApiRequest,
        *,
        user_inputs: list[str] | None,
        api_key: str | None,
        action_results: list[str] | None,
    ) -> ApiRequest:
        kwargs = {
            "user_inputs": user_inputs,
            "action_results": action_results,
            "api_key": api_key,
        }
        return ApiRequest(
            name=template.name,
            method=template.method,
            url=self._resolver.resolve(template.url, **kwargs),
            headers=self._resolver.resolve_in_object(template.headers, **kwargs),
            body=self._resolver.resolve_in_object(template.body, **kwargs),
            response_path=template.response_path,
            description=template.description,
        )
