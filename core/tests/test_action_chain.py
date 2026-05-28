from __future__ import annotations

from pathlib import Path

import pytest

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
