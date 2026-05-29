from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ActionStep:
    """One step in an action chain: which config path to run and its input placeholders."""

    config: str  # relative path to single config (e.g. "configs/singles/echo.yaml")
    inputs: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ActionChain:
    """A named sequence of ActionStep definitions."""

    title: str
    steps: list[ActionStep]
    note: str = ""
