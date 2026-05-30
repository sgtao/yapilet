from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class AppStore:
    """Single source of truth for cross-page state.

    api_key  : Settings で設定。send() ごとにライブ反映。
    mock_echo: Settings で設定。[Load] 時に use case が再生成されて反映。
    """

    api_key: str = ""
    mock_echo: bool = False

    def get_api_key(self) -> str | None:
        """Return api_key if set, else fall back to API_KEY env var."""
        return self.api_key or os.getenv("API_KEY") or None
