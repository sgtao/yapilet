from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from yapilet.core.models.action_chain import ActionChain, ActionStep
from yapilet.core.models.api_request import ApiRequest
from yapilet.core.models.messages_request import MessagesRequest


class ConfigLoader:
    """Loads YAML configs by path into domain models."""

    def __init__(self, configs_dir: Path | None = None) -> None:
        self._configs_dir = configs_dir  # reserved for GUI list_singles()

    def load_single(self, path: Path) -> ApiRequest:
        """Load a single_config YAML at `path` and return ApiRequest."""
        if not path.exists():
            raise FileNotFoundError(f"Single config not found: {path}")
        with path.open("r", encoding="utf-8") as f:
            raw: dict[str, Any] = yaml.safe_load(f) or {}

        title = str(raw.get("title", path.stem))
        note = str(raw.get("note", ""))
        cfg: dict[str, Any] = raw.get("single_config", {})

        return ApiRequest(
            title=title,
            note=note,
            method=str(cfg.get("method", "GET")).upper(),
            url=str(cfg.get("url") or cfg.get("uri", "")),
            headers=self._parse_headers(cfg),
            body=dict(cfg.get("body") or cfg.get("req_body") or {}),
            response_path=cfg.get("response_path") or cfg.get("user_property_path"),
        )

    def load_action(self, path: Path) -> ActionChain:
        """Load an action_config YAML at `path` and return ActionChain."""
        if not path.exists():
            raise FileNotFoundError(f"Action config not found: {path}")
        with path.open("r", encoding="utf-8") as f:
            raw: dict[str, Any] = yaml.safe_load(f) or {}

        title = str(raw.get("title", path.stem))
        note = str(raw.get("note", ""))
        cfg: dict[str, Any] = raw.get("action_config", {})
        steps = [
            ActionStep(
                config=str(s["config"]),
                inputs=[str(i) for i in s.get("inputs", [])],
            )
            for s in cfg.get("steps", [])
        ]
        return ActionChain(title=title, steps=steps, note=note)

    def load_messages(self, path: Path) -> MessagesRequest:
        """Load a messages_config YAML at `path` and return MessagesRequest."""
        if not path.exists():
            raise FileNotFoundError(f"Messages config not found: {path}")
        with path.open("r", encoding="utf-8") as f:
            raw: dict[str, Any] = yaml.safe_load(f) or {}

        title = str(raw.get("title", path.stem))
        note = str(raw.get("note", ""))
        cfg: dict[str, Any] = raw.get("messages_config", {})

        url = str(cfg.get("url") or cfg.get("uri", ""))
        headers = self._parse_headers(cfg)
        messages = [dict(m) for m in cfg.get("messages", [])]
        response_path: str | None = cfg.get("response_path") or cfg.get("user_property_path")

        _known = {"url", "uri", "headers", "header_df", "messages", "response_path", "user_property_path"}
        body_extra: dict[str, Any] = {k: v for k, v in cfg.items() if k not in _known}

        return MessagesRequest(
            title=title,
            note=note,
            url=url,
            headers=headers,
            messages=messages,
            body_extra=body_extra,
            response_path=response_path,
        )

    @staticmethod
    def _parse_headers(cfg: dict[str, Any]) -> dict[str, str]:
        """Support both headers: dict and header_df: list formats."""
        if "headers" in cfg:
            return dict(cfg["headers"])
        if "header_df" in cfg:
            return {str(item["Property"]): str(item["Value"]) for item in cfg["header_df"]}
        return {}

    @property
    def singles_dir(self) -> Path | None:
        return self._configs_dir / "singles" if self._configs_dir else None

    def list_singles(self) -> list[str]:
        """Return sorted stems for GUI file browser (requires configs_dir)."""
        if not self.singles_dir or not self.singles_dir.exists():
            return []
        return sorted(p.stem for p in self.singles_dir.glob("*.yaml"))
