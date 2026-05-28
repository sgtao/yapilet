from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from yapilet.core.models.api_request import ApiRequest


@dataclass(frozen=True)
class RawResponse:
    """Transport-level response shape, before domain interpretation."""

    status_code: int
    body: Any
    headers: dict[str, str] = field(default_factory=dict)


class HttpPort(ABC):
    """Abstraction of outbound HTTP. Implementations live in infrastructure/."""

    @abstractmethod
    def send(self, request: ApiRequest) -> RawResponse:
        """Send an already-expanded request and return the raw response."""
        raise NotImplementedError
