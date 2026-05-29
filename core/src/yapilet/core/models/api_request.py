from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ApiRequest:
    """Definition of a single API request (template; placeholders not yet expanded)."""

    title: str
    method: str  # GET / POST / PUT / DELETE
    url: str
    headers: dict[str, str] = field(default_factory=dict)
    body: dict[str, Any] = field(default_factory=dict)
    response_path: str | None = None  # jmespath expression
    note: str = ""
