from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from yapilet.core.application.execute_action import ExecuteActionUseCase
from yapilet.core.application.execute_chat import ExecuteChatUseCase
from yapilet.core.application.execute_single import ExecuteSingleUseCase
from yapilet.core.infrastructure.httpx_adapter import HttpxAdapter
from yapilet.core.infrastructure.mock_adapter import MockAdapter
from yapilet.core.models.action_chain import ActionChain as ActionChain  # pages への re-export 用
from yapilet.core.models.api_request import ApiRequest
from yapilet.core.services.config_loader import ConfigLoader
from yapilet.gui.app_store import AppStore

_CONFIGS_ROOT = Path("configs")
_PRIVATES_ROOT = Path("privates")

_PLACEHOLDER_RE = re.compile(r"[<＜]user_input_(\d+)[>＞]|\{\{\s*user_input_(\d+)\s*\}\}")


def _glob_yamls(*dirs: Path) -> list[Path]:
    """Collect *.yaml from each directory if it exists, sorted by name."""
    results: list[Path] = []
    for d in dirs:
        if d.exists():
            results.extend(sorted(d.glob("*.yaml")))
    return results


def list_single_configs() -> list[Path]:
    return _glob_yamls(
        _CONFIGS_ROOT / "singles",
        _PRIVATES_ROOT / "singles",
    )


def list_action_configs() -> list[Path]:
    return _glob_yamls(
        _CONFIGS_ROOT / "actions",
        _PRIVATES_ROOT / "actions",
    )


def list_chat_configs() -> list[Path]:
    """Chat 用設定リスト。body.messages を持たない config が混在する可能性あり。"""
    return _glob_yamls(
        _CONFIGS_ROOT / "singles",
        _CONFIGS_ROOT / "messages",
        _PRIVATES_ROOT / "singles",
        _PRIVATES_ROOT / "messages",
    )


def make_single_usecase(store: AppStore) -> ExecuteSingleUseCase:
    http_port = MockAdapter() if store.mock_echo else HttpxAdapter()
    return ExecuteSingleUseCase(http_port=http_port, config_loader=ConfigLoader())


def make_action_usecase(store: AppStore) -> ExecuteActionUseCase:
    single = make_single_usecase(store)
    return ExecuteActionUseCase(single_usecase=single, config_loader=ConfigLoader())


def make_chat_usecase(store: AppStore) -> ExecuteChatUseCase:
    http_port = MockAdapter() if store.mock_echo else HttpxAdapter()
    return ExecuteChatUseCase(http_port=http_port, config_loader=ConfigLoader())


def load_single_config(path: Path) -> ApiRequest:
    """pages から呼ぶ単発 config ローダー。pages が core.services を直接 import しない。"""
    return ConfigLoader().load_single(path)


def load_action_config(path: Path) -> ActionChain:
    """pages から呼ぶ action config ローダー。"""
    return ConfigLoader().load_action(path)


def _flatten_values(obj: Any) -> list[str]:
    if isinstance(obj, str):
        return [obj]
    if isinstance(obj, dict):
        out: list[str] = []
        for v in obj.values():
            out.extend(_flatten_values(v))
        return out
    if isinstance(obj, list):
        out = []
        for v in obj:
            out.extend(_flatten_values(v))
        return out
    return [str(obj)] if obj is not None else []


def count_user_inputs(request: ApiRequest) -> int:
    """Return the number of user_input_N placeholders in the request template."""
    texts = [request.url] + list(request.headers.values()) + _flatten_values(request.body)
    indices: set[int] = set()
    for text in texts:
        for m in _PLACEHOLDER_RE.finditer(text):
            raw = m.group(1) if m.group(1) is not None else m.group(2)
            indices.add(int(raw))
    return max(indices) + 1 if indices else 0
