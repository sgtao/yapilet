from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from yapilet.core.application.execute_action import ExecuteActionUseCase
from yapilet.core.application.execute_single import ExecuteSingleUseCase
from yapilet.core.infrastructure.mock_adapter import MockAdapter
from yapilet.core.models.result import Result
from yapilet.core.services.config_loader import ConfigLoader


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _write_echo_yaml(configs_dir: Path) -> None:
    """Write the echo single config in new single_config: format."""
    _write(
        configs_dir / "singles" / "echo.yaml",
        """
title: echo
note: "Mock-friendly echo request for smoke testing"
single_config:
  method: POST
  url: "https://example.com/echo"
  headers:
    Authorization: "Bearer ＜API_KEY＞"
  body:
    message: "＜user_input_0＞"
  response_path: "echo.body.message"
""".strip(),
    )


def _make_uc(tmp_path: Path) -> ExecuteActionUseCase:
    return ExecuteActionUseCase(
        single_usecase=ExecuteSingleUseCase(
            http_port=MockAdapter(),
            config_loader=ConfigLoader(),
        ),
        config_loader=ConfigLoader(),
    )


# --- ConfigLoader.load_action tests ---

def test_load_action_parses_steps(tmp_path: Path) -> None:
    _write(
        tmp_path / "actions" / "echo_chain.yaml",
        f"""
title: echo_chain
note: two-step echo
action_config:
  steps:
    - config: "{tmp_path / "singles" / "echo.yaml"}"
      inputs:
        - "＜user_input_0＞"
    - config: "{tmp_path / "singles" / "echo.yaml"}"
      inputs:
        - "＜action_result_0＞"
""".strip(),
    )
    loader = ConfigLoader()
    chain = loader.load_action(tmp_path / "actions" / "echo_chain.yaml")
    assert chain.title == "echo_chain"
    assert len(chain.steps) == 2
    assert chain.steps[0].inputs == ["＜user_input_0＞"]
    assert chain.steps[1].inputs == ["＜action_result_0＞"]


def test_load_action_missing_raises(tmp_path: Path) -> None:
    loader = ConfigLoader()
    with pytest.raises(FileNotFoundError):
        loader.load_action(tmp_path / "nope.yaml")


# --- ExecuteActionUseCase tests ---

def test_execute_action_single_step(tmp_path: Path) -> None:
    _write_echo_yaml(tmp_path)
    echo_path = str(tmp_path / "singles" / "echo.yaml")
    _write(
        tmp_path / "actions" / "single.yaml",
        f"""
title: single
action_config:
  steps:
    - config: "{echo_path}"
      inputs:
        - "＜user_input_0＞"
""".strip(),
    )
    uc = _make_uc(tmp_path)
    results = uc.run(
        str(tmp_path / "actions" / "single.yaml"),
        user_inputs=["hello"],
        api_key="sk-demo",
    )
    assert len(results) == 1
    assert results[0].is_success
    assert results[0].extracted == "hello"


def test_execute_action_passes_result_to_next_step(tmp_path: Path) -> None:
    _write_echo_yaml(tmp_path)
    echo_path = str(tmp_path / "singles" / "echo.yaml")
    _write(
        tmp_path / "actions" / "chain.yaml",
        f"""
title: chain
action_config:
  steps:
    - config: "{echo_path}"
      inputs:
        - "＜user_input_0＞"
    - config: "{echo_path}"
      inputs:
        - "＜action_result_0＞"
""".strip(),
    )
    uc = _make_uc(tmp_path)
    results = uc.run(
        str(tmp_path / "actions" / "chain.yaml"),
        user_inputs=["hello"],
        api_key="sk-demo",
    )
    assert len(results) == 2
    assert results[0].extracted == "hello"
    assert results[1].extracted == "hello"


def test_execute_action_out_of_range_action_result_raises(tmp_path: Path) -> None:
    _write_echo_yaml(tmp_path)
    echo_path = str(tmp_path / "singles" / "echo.yaml")
    _write(
        tmp_path / "actions" / "bad.yaml",
        f"""
title: bad
action_config:
  steps:
    - config: "{echo_path}"
      inputs:
        - "＜action_result_0＞"
""".strip(),
    )
    uc = _make_uc(tmp_path)
    with pytest.raises(ValueError, match="action_result index 0 out of range"):
        uc.run(str(tmp_path / "actions" / "bad.yaml"), user_inputs=["hello"])


def test_execute_action_delegates_to_single(tmp_path: Path) -> None:
    """ExecuteActionUseCase が ExecuteSingleUseCase.run() に委譲することを確認する。"""
    _write_echo_yaml(tmp_path)
    echo_path = str(tmp_path / "singles" / "echo.yaml")
    _write(
        tmp_path / "actions" / "chain.yaml",
        f"""
title: chain
action_config:
  steps:
    - config: "{echo_path}"
      inputs:
        - "＜user_input_0＞"
    - config: "{echo_path}"
      inputs:
        - "＜action_result_0＞"
""".strip(),
    )

    mock_single = MagicMock(spec=ExecuteSingleUseCase)
    mock_single.run.return_value = Result(
        status_code=200, body={}, extracted="mocked", is_success=True
    )

    uc = ExecuteActionUseCase(
        single_usecase=mock_single,
        config_loader=ConfigLoader(),
    )
    results = uc.run(
        str(tmp_path / "actions" / "chain.yaml"),
        user_inputs=["hello"],
        api_key="sk-demo",
    )

    assert len(results) == 2
    assert mock_single.run.call_count == 2
    first_call = mock_single.run.call_args_list[0]
    assert first_call.kwargs["user_inputs"] == ["hello"]
    second_call = mock_single.run.call_args_list[1]
    assert second_call.kwargs["user_inputs"] == ["mocked"]
    assert "action_results" not in first_call.kwargs
