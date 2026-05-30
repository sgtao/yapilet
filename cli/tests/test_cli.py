from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner
from yapilet.cli.main import cli
from yapilet.core.models.result import Result


@pytest.fixture()
def configs_dir(tmp_path: Path) -> Path:
    singles = tmp_path / "singles"
    singles.mkdir(parents=True)
    (singles / "echo.yaml").write_text(
        """
title: echo
note: "Mock-friendly echo"
single_config:
  method: POST
  url: "https://example.com/echo"
  headers:
    Authorization: "Bearer ＜API_KEY＞"
  body:
    message: "＜user_input_0＞"
  response_path: "echo.body.message"
""".strip(),
        encoding="utf-8",
    )
    actions = tmp_path / "actions"
    actions.mkdir()
    echo_path = str(singles / "echo.yaml")
    (actions / "echo_chain.yaml").write_text(
        f"""
title: echo_chain
action_config:
  steps:
    - config: "{echo_path}"
      inputs:
        - "＜user_input_0＞"
    - config: "{echo_path}"
      inputs:
        - "＜action_result_0＞"
""".strip(),
        encoding="utf-8",
    )
    return tmp_path


def test_single_mock_echo_outputs_extracted(configs_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["single", str(configs_dir / "singles" / "echo.yaml"),
         "--user-input", "hello", "--mock-echo"],
    )
    assert result.exit_code == 0
    assert result.output.strip() == "hello"


def test_single_missing_config_exits_nonzero(configs_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["single", str(configs_dir / "singles" / "nope.yaml"), "--mock-echo"],
    )
    assert result.exit_code != 0


def test_action_mock_echo_outputs_each_step(configs_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["action", str(configs_dir / "actions" / "echo_chain.yaml"),
         "--user-input", "hello", "--mock-echo"],
    )
    assert result.exit_code == 0
    lines = result.output.strip().splitlines()
    assert len(lines) == 2
    assert "hello" in lines[0]
    assert "hello" in lines[1]


def test_action_missing_chain_exits_nonzero(configs_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["action", str(configs_dir / "actions" / "nope.yaml"), "--mock-echo"],
    )
    assert result.exit_code != 0


def test_single_no_response_path_outputs_json(tmp_path: Path) -> None:
    p = tmp_path / "bare.yaml"
    p.write_text(
        """
title: bare
single_config:
  method: GET
  url: https://example.com
  body:
    msg: hi
""".strip(),
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["single", str(p), "--mock-echo"],
    )
    assert result.exit_code == 0
    assert "{" in result.output


def test_api_key_passed_to_usecase(configs_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["single", str(configs_dir / "singles" / "echo.yaml"),
         "--user-input", "hello", "--api-key", "sk-test", "--mock-echo"],
    )
    assert result.exit_code == 0
    assert result.output.strip() == "hello"


def test_single_error_result_exits_nonzero(configs_dir: Path) -> None:
    fail_result = Result(
        status_code=500,
        body=None,
        extracted=None,
        is_success=False,
        error="Internal Server Error",
    )
    runner = CliRunner()
    with patch(
        "yapilet.cli.main.make_single_usecase"
    ) as mock_make_uc:
        mock_uc = MagicMock()
        mock_uc.run.return_value = fail_result
        mock_make_uc.return_value = mock_uc
        result = runner.invoke(
            cli,
            ["single", str(configs_dir / "singles" / "echo.yaml"), "--mock-echo"],
        )
    assert result.exit_code != 0


def test_action_step_error_exits_nonzero(configs_dir: Path) -> None:
    fail_result = Result(
        status_code=500,
        body=None,
        extracted=None,
        is_success=False,
        error="step failed",
    )
    runner = CliRunner()
    with patch(
        "yapilet.cli.main.make_action_usecase"
    ) as mock_make_uc:
        mock_uc = MagicMock()
        mock_uc.run.return_value = [fail_result, fail_result]  # 2 steps to match chain length
        mock_make_uc.return_value = mock_uc
        result = runner.invoke(
            cli,
            ["action", str(configs_dir / "actions" / "echo_chain.yaml"), "--mock-echo"],
        )
    assert result.exit_code != 0
