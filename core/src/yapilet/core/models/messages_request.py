from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class MessagesRequest:
    """Chat-style API request (OpenAI-compatible messages array)."""

    title: str
    url: str
    messages: list[dict[str, Any]]
    headers: dict[str, str] = field(default_factory=dict)
    body_extra: dict[str, Any] = field(default_factory=dict)
    response_path: str | None = None
    note: str = ""
