from __future__ import annotations

from pathlib import Path

import pytest

from yapilet.core.services.config_loader import ConfigLoader


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_list_singles_empty(tmp_path: Path) -> None:
    loader = ConfigLoader(tmp_path)
    assert loader.list_singles() == []


def test_list_singles_returns_sorted_stems(tmp_path: Path) -> None:
    _write(tmp_path / "singles" / "b.yaml", "name: b\nmethod: GET\nurl: http://x\n")
    _write(tmp_path / "singles" / "a.yaml", "name: a\nmethod: GET\nurl: http://x\n")
    loader = ConfigLoader(tmp_path)
    assert loader.list_singles() == ["a", "b"]


def test_load_single_parses_fields(tmp_path: Path) -> None:
    _write(
        tmp_path / "singles" / "echo.yaml",
        """
name: echo
description: test
method: post
url: "https://example.com/x"
headers:
  Authorization: "Bearer ＜API_KEY＞"
body:
  message: "＜user_input_0＞"
response_path: "echo.body.message"
""".strip(),
    )
    loader = ConfigLoader(tmp_path)
    req = loader.load_single("echo")
    assert req.name == "echo"
    assert req.method == "POST"  # uppercased
    assert req.url == "https://example.com/x"
    assert req.headers["Authorization"] == "Bearer ＜API_KEY＞"
    assert req.body["message"] == "＜user_input_0＞"
    assert req.response_path == "echo.body.message"


def test_load_single_missing_raises(tmp_path: Path) -> None:
    loader = ConfigLoader(tmp_path)
    with pytest.raises(FileNotFoundError):
        loader.load_single("nope")
