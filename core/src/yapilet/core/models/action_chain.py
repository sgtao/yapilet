from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ActionStep:
    """One step in an action chain: which single config to run and its input placeholders."""

    config: str
    inputs: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ActionChain:
    """A named sequence of ActionStep definitions."""

    name: str
    steps: list[ActionStep]
    description: str = ""
