from __future__ import annotations

from pathlib import Path

import pytest
from yapilet.core.services.config_loader import ConfigLoader


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_load_single_parses_single_config_wrapper(tmp_path: Path) -> None:
    p = tmp_path / "echo.yaml"
    _write(p, """
title: echo
note: "test note"
single_config:
  method: POST
  url: "https://example.com/echo"
  headers:
    Authorization: "Bearer ＜API_KEY＞"
  body:
    message: "＜user_input_0＞"
  response_path: "echo.body.message"
""".strip())
    req = ConfigLoader().load_single(p)
    assert req.title == "echo"
    assert req.note == "test note"
    assert req.method == "POST"
    assert req.url == "https://example.com/echo"
    assert req.headers["Authorization"] == "Bearer ＜API_KEY＞"
    assert req.body["message"] == "＜user_input_0＞"
    assert req.response_path == "echo.body.message"


def test_load_single_field_aliases(tmp_path: Path) -> None:
    p = tmp_path / "old.yaml"
    _write(p, """
title: old format
single_config:
  method: POST
  uri: "https://api.example.com"
  header_df:
    - Property: Authorization
      Value: "Bearer ＜API_KEY＞"
  req_body:
    message: "＜user_input_0＞"
  user_property_path: "choices[0].message.content"
""".strip())
    req = ConfigLoader().load_single(p)
    assert req.url == "https://api.example.com"
    assert req.headers["Authorization"] == "Bearer ＜API_KEY＞"
    assert req.body["message"] == "＜user_input_0＞"
    assert req.response_path == "choices[0].message.content"


def test_load_single_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        ConfigLoader().load_single(tmp_path / "nope.yaml")


def test_load_action_parses_action_config_wrapper(tmp_path: Path) -> None:
    p = tmp_path / "echo_chain.yaml"
    _write(p, """
title: echo_chain
note: "two-step"
action_config:
  steps:
    - config: "configs/singles/echo.yaml"
      inputs:
        - "＜user_input_0＞"
    - config: "configs/singles/echo.yaml"
      inputs:
        - "＜action_result_0＞"
""".strip())
    chain = ConfigLoader().load_action(p)
    assert chain.title == "echo_chain"
    assert chain.note == "two-step"
    assert len(chain.steps) == 2
    assert chain.steps[0].config == "configs/singles/echo.yaml"
    assert chain.steps[0].inputs == ["＜user_input_0＞"]
    assert chain.steps[1].inputs == ["＜action_result_0＞"]


def test_load_action_missing_raises(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        ConfigLoader().load_action(tmp_path / "nope.yaml")
