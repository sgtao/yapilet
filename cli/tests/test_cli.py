from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner
from yapilet.cli.main import cli


@pytest.fixture()
def configs_dir(tmp_path: Path) -> Path:
    singles = tmp_path / "singles"
    singles.mkdir(parents=True)
    (singles / "echo.yaml").write_text(
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
        encoding="utf-8",
    )
    actions = tmp_path / "actions"
    actions.mkdir()
    (actions / "echo_chain.yaml").write_text(
        """
name: echo_chain
steps:
  - config: echo
    inputs:
      - "＜user_input_0＞"
  - config: echo
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
        ["single", "echo", "--user-input", "hello", "--mock-echo",
         "--configs-dir", str(configs_dir)],
    )
    assert result.exit_code == 0
    assert result.output.strip() == "hello"


def test_single_missing_config_exits_nonzero(configs_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["single", "nope", "--mock-echo", "--configs-dir", str(configs_dir)],
    )
    assert result.exit_code != 0


def test_action_mock_echo_outputs_each_step(configs_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["action", "echo_chain", "--user-input", "hello", "--mock-echo",
         "--configs-dir", str(configs_dir)],
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
        ["action", "nope", "--mock-echo", "--configs-dir", str(configs_dir)],
    )
    assert result.exit_code != 0


def test_single_no_response_path_outputs_json(tmp_path: Path) -> None:
    singles = tmp_path / "singles"
    singles.mkdir()
    (singles / "bare.yaml").write_text(
        "name: bare\nmethod: GET\nurl: https://example.com\nbody:\n  msg: hi\n",
        encoding="utf-8",
    )
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["single", "bare", "--mock-echo", "--configs-dir", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert "{" in result.output


def test_api_key_passed_to_usecase(configs_dir: Path) -> None:
    runner = CliRunner()
    result = runner.invoke(
        cli,
        ["single", "echo", "--user-input", "hello",
         "--api-key", "sk-test", "--mock-echo",
         "--configs-dir", str(configs_dir)],
    )
    assert result.exit_code == 0
    assert result.output.strip() == "hello"
