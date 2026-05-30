from __future__ import annotations

from pathlib import Path
from typing import Any

from yapilet.core.models.api_request import ApiRequest
from yapilet.core.ports.http_port import HttpPort
from yapilet.core.services.api_client import ApiClient
from yapilet.core.services.config_loader import ConfigLoader
from yapilet.core.services.placeholder import PlaceholderResolver


class ExecuteChatUseCase:
    """Stateful multi-turn chat use case.

    Loads a single_config: YAML whose body contains a "messages" array
    (seed: system prompt, examples, etc.). Each send() call appends the
    user message, sends the full history, and appends the assistant reply.
    """

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
        self._template: ApiRequest | None = None
        self._history: list[dict[str, Any]] = []

    def load(self, config_path: str | Path) -> None:
        """Load single_config YAML and initialize history from seed messages."""
        self._template = self._loader.load_single(Path(config_path))
        seed = self._template.body.get("messages", [])
        self._history = [dict(m) for m in seed]

    def send(self, user_input: str, *, api_key: str | None = None) -> str | None:
        """Append user message, call API, append assistant reply, return extracted text."""
        if self._template is None:
            raise RuntimeError("Call load() before send()")

        self._history.append({"role": "user", "content": user_input})

        body: dict[str, Any] = {
            k: v for k, v in self._template.body.items() if k != "messages"
        }
        body["messages"] = list(self._history)

        resolved_headers: dict[str, str] = self._resolver.resolve_in_object(
            dict(self._template.headers), api_key=api_key
        )
        resolved_url: str = self._resolver.resolve(
            self._template.url, api_key=api_key
        )

        request = ApiRequest(
            title=self._template.title,
            method=self._template.method,
            url=resolved_url,
            headers=resolved_headers,
            body=body,
            response_path=self._template.response_path,
            note=self._template.note,
        )

        result = self._client.send(request)

        if not result.is_success:
            self._history.pop()  # undo user message on failure
            return None

        assistant_text = str(result.extracted) if result.extracted is not None else ""
        self._history.append({"role": "assistant", "content": assistant_text})
        return assistant_text

    @property
    def history(self) -> list[dict[str, Any]]:
        """Current conversation history (read-only copy)."""
        return list(self._history)
