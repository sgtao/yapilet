from __future__ import annotations

from pathlib import Path

import pytest
from yapilet.core.application.execute_chat import ExecuteChatUseCase
from yapilet.core.infrastructure.mock_adapter import MockAdapter
from yapilet.core.services.config_loader import ConfigLoader


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_chat_config(tmp_path: Path) -> Path:
    p = tmp_path / "chat.yaml"
    _write(p, """
title: test_chat
single_config:
  method: POST
  url: "https://example.com/v1/chat/completions"
  headers:
    Authorization: "Bearer ＜API_KEY＞"
  body:
    model: "test-model"
    messages:
      - role: "system"
        content: "You are helpful."
  response_path: "echo.body.messages[-1].content"
""".strip())
    return p


def test_load_initializes_history_from_seed(tmp_path: Path) -> None:
    uc = ExecuteChatUseCase(http_port=MockAdapter(), config_loader=ConfigLoader())
    uc.load(_make_chat_config(tmp_path))
    assert uc.history == [{"role": "system", "content": "You are helpful."}]


def test_send_appends_user_and_assistant_messages(tmp_path: Path) -> None:
    uc = ExecuteChatUseCase(http_port=MockAdapter(), config_loader=ConfigLoader())
    uc.load(_make_chat_config(tmp_path))
    response = uc.send("hello", api_key="sk-test")
    assert response == "hello"
    assert uc.history[-2] == {"role": "user", "content": "hello"}
    assert uc.history[-1] == {"role": "assistant", "content": "hello"}


def test_send_second_turn_accumulates_history(tmp_path: Path) -> None:
    uc = ExecuteChatUseCase(http_port=MockAdapter(), config_loader=ConfigLoader())
    uc.load(_make_chat_config(tmp_path))
    uc.send("first", api_key="sk-test")
    uc.send("second", api_key="sk-test")
    roles = [m["role"] for m in uc.history]
    assert roles == ["system", "user", "assistant", "user", "assistant"]


def test_send_before_load_raises(tmp_path: Path) -> None:
    uc = ExecuteChatUseCase(http_port=MockAdapter(), config_loader=ConfigLoader())
    with pytest.raises(RuntimeError, match="load\\(\\)"):
        uc.send("hello")


def test_send_api_key_resolved_in_headers(tmp_path: Path) -> None:
    uc = ExecuteChatUseCase(http_port=MockAdapter(), config_loader=ConfigLoader())
    uc.load(_make_chat_config(tmp_path))
    uc.send("hi", api_key="sk-test")
    assert uc.history[-1]["role"] == "assistant"
