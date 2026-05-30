from __future__ import annotations

from pathlib import Path

import pytest
from yapilet.core.application.execute_messages import ExecuteMessagesUseCase
from yapilet.core.infrastructure.mock_adapter import MockAdapter
from yapilet.core.services.config_loader import ConfigLoader


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _make_chat_yaml(tmp_path: Path, *, response_path: str = "echo.body.messages[-1].content") -> Path:
    p = tmp_path / "chat.yaml"
    _write(p, f"""
title: test_chat
messages_config:
  url: "https://example.com/v1/messages"
  model: "test-model"
  messages:
    - role: "user"
      content: "＜user_input_0＞"
  response_path: "{response_path}"
""".strip())
    return p


def test_execute_messages_resolves_user_input(tmp_path: Path) -> None:
    p = _make_chat_yaml(tmp_path)
    uc = ExecuteMessagesUseCase(
        http_port=MockAdapter(),
        config_loader=ConfigLoader(),
    )
    result = uc.run(str(p), user_inputs=["hello world"])
    assert result.is_success
    assert result.extracted == "hello world"


def test_execute_messages_resolves_api_key_in_headers(tmp_path: Path) -> None:
    p = tmp_path / "chat_auth.yaml"
    _write(p, """
title: auth_chat
messages_config:
  url: "https://example.com/v1/messages"
  headers:
    Authorization: "Bearer ＜API_KEY＞"
  model: "test-model"
  messages:
    - role: "user"
      content: "＜user_input_0＞"
  response_path: "echo.body.messages[-1].content"
""".strip())
    uc = ExecuteMessagesUseCase(
        http_port=MockAdapter(),
        config_loader=ConfigLoader(),
    )
    result = uc.run(str(p), user_inputs=["hi"], api_key="sk-test")
    assert result.is_success
    assert result.body["echo"]["headers"]["Authorization"] == "Bearer sk-test"


def test_execute_messages_body_extra_merged_into_body(tmp_path: Path) -> None:
    p = _make_chat_yaml(tmp_path)
    uc = ExecuteMessagesUseCase(
        http_port=MockAdapter(),
        config_loader=ConfigLoader(),
    )
    result = uc.run(str(p), user_inputs=["x"])
    assert result.body["echo"]["body"]["model"] == "test-model"


def test_execute_messages_file_not_found(tmp_path: Path) -> None:
    uc = ExecuteMessagesUseCase(
        http_port=MockAdapter(),
        config_loader=ConfigLoader(),
    )
    with pytest.raises(FileNotFoundError):
        uc.run(str(tmp_path / "nope.yaml"))
