from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from yapilet.core.models.api_request import ApiRequest


class ConfigLoader:
    """Loads YAML configs under configs/singles/ into ApiRequest models."""

    def __init__(self, configs_dir: Path) -> None:
        self._configs_dir = configs_dir

    @property
    def singles_dir(self) -> Path:
        return self._configs_dir / "singles"

    def list_singles(self) -> list[str]:
        """Return sorted names of available single configs (filename stems)."""
        if not self.singles_dir.exists():
            return []
        return sorted(p.stem for p in self.singles_dir.glob("*.yaml"))

    def load_single(self, name: str) -> ApiRequest:
        """Load a single config by name (filename stem) and return ApiRequest."""
        path = self.singles_dir / f"{name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Single config not found: {path}")
        with path.open("r", encoding="utf-8") as f:
            raw: dict[str, Any] = yaml.safe_load(f) or {}
        return ApiRequest(
            name=raw.get("name", name),
            method=str(raw.get("method", "GET")).upper(),
            url=str(raw.get("url", "")),
            headers=dict(raw.get("headers", {})),
            body=dict(raw.get("body", {})),
            response_path=raw.get("response_path"),
            description=str(raw.get("description", "")),
        )
