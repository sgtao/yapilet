from __future__ import annotations

from pathlib import Path

import pytest

from yapilet.core.application.execute_action import ExecuteActionUseCase
from yapilet.core.infrastructure.mock_adapter import MockAdapter
from yapilet.core.models.action_chain import ActionChain, ActionStep
from yapilet.core.services.config_loader import ConfigLoader


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_load_action_parses_steps(tmp_path: Path) -> None:
    _write(
        tmp_path / "actions" / "echo_chain.yaml",
        """
name: echo_chain
description: two-step echo
steps:
  - config: echo
    inputs:
      - "＜user_input_0＞"
  - config: echo
    inputs:
      - "＜action_result_0＞"
""".strip(),
    )
    loader = ConfigLoader(tmp_path)
    chain = loader.load_action("echo_chain")
    assert chain.name == "echo_chain"
    assert len(chain.steps) == 2
    assert chain.steps[0].config == "echo"
    assert chain.steps[0].inputs == ["＜user_input_0＞"]
    assert chain.steps[1].inputs == ["＜action_result_0＞"]


def test_load_action_missing_raises(tmp_path: Path) -> None:
    loader = ConfigLoader(tmp_path)
    with pytest.raises(FileNotFoundError):
        loader.load_action("nope")


# --- ExecuteActionUseCase tests ---

def _write_echo_yaml(configs_dir: Path) -> None:
    """Write the echo single config needed by chain tests."""
    _write(
        configs_dir / "singles" / "echo.yaml",
        """
name: echo
method: POST
url: "https://example.com/echo"
headers:
  Authorization: "Bearer ＜API_KEY＞"
body:
  message: "＜user_input_0＞"
response_path: "echo.body.message"
""".strip(),
    )


def test_execute_action_single_step(tmp_path: Path) -> None:
    _write_echo_yaml(tmp_path)
    _write(
        tmp_path / "actions" / "single.yaml",
        "name: single\nsteps:\n  - config: echo\n    inputs:\n      - \"＜user_input_0＞\"\n",
    )
    uc = ExecuteActionUseCase(
        http_port=MockAdapter(),
        config_loader=ConfigLoader(tmp_path),
    )
    results = uc.run("single", user_inputs=["hello"], api_key="sk-demo")
    assert len(results) == 1
    assert results[0].is_success
    assert results[0].extracted == "hello"


def test_execute_action_passes_result_to_next_step(tmp_path: Path) -> None:
    _write_echo_yaml(tmp_path)
    _write(
        tmp_path / "actions" / "chain.yaml",
        """
name: chain
steps:
  - config: echo
    inputs:
      - "＜user_input_0＞"
  - config: echo
    inputs:
      - "＜action_result_0＞"
""".strip(),
    )
    uc = ExecuteActionUseCase(
        http_port=MockAdapter(),
        config_loader=ConfigLoader(tmp_path),
    )
    results = uc.run("chain", user_inputs=["hello"], api_key="sk-demo")
    assert len(results) == 2
    assert results[0].extracted == "hello"
    assert results[1].extracted == "hello"  # step 2 received step 1's result


def test_execute_action_out_of_range_action_result_raises(tmp_path: Path) -> None:
    _write_echo_yaml(tmp_path)
    _write(
        tmp_path / "actions" / "bad.yaml",
        "name: bad\nsteps:\n  - config: echo\n    inputs:\n      - \"＜action_result_0＞\"\n",
    )
    uc = ExecuteActionUseCase(
        http_port=MockAdapter(),
        config_loader=ConfigLoader(tmp_path),
    )
    with pytest.raises(ValueError, match="action_result index 0 out of range"):
        uc.run("bad", user_inputs=["hello"])
