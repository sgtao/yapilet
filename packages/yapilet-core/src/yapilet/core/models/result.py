from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Result:
    """Outcome of executing one API request."""

    status_code: int
    body: Any  # parsed response body (dict / list / str)
    extracted: Any = None  # result of applying response_path
    is_success: bool = False
    error: str | None = None
    raw_headers: dict[str, str] = field(default_factory=dict)
