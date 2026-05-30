from __future__ import annotations

import json

import flet as ft
from yapilet.gui._di import (
    count_user_inputs,
    list_single_configs,
    load_single_config,
    make_single_usecase,
)
from yapilet.gui.app_store import AppStore


class SinglePage(ft.Column):
    """Single Request: YAML 設定を選んでリクエストを実行する。"""

    def __init__(self, store: AppStore) -> None:
        super().__init__(scroll=ft.ScrollMode.AUTO, expand=True, spacing=8)
        self._store = store

        configs = list_single_configs()
        self._config_paths = {p.stem: p for p in configs}

        self._config_dropdown = ft.Dropdown(
            label="Config ファイル",
            options=[ft.dropdown.Option(stem) for stem in self._config_paths],
            expand=True,
            on_select=self._on_config_changed,  # type: ignore[arg-type]
        )
        self._title_text = ft.Text("", size=14, weight=ft.FontWeight.W_600)
        self._note_text = ft.Text("", size=12, color=ft.Colors.GREY_600, selectable=True)
        self._input_column = ft.Column([], spacing=8)
        self._run_button = ft.ElevatedButton(
            "▶ Run",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self._on_run,  # type: ignore[arg-type]
            disabled=True,
        )
        self._response_text = ft.Text("", selectable=True)
        self._raw_json_text = ft.Text("", selectable=True, visible=False, size=11)
        self._response_tile = ft.ExpansionTile(
            title=ft.Text("レスポンス"),
            expanded=False,
            controls=[self._response_text, self._raw_json_text],
        )

        self.controls = [
            ft.Text("Single Request", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row([self._config_dropdown]),
            ft.ExpansionTile(
                title=ft.Text("設定内容"),
                expanded=False,
                controls=[self._title_text, self._note_text],
            ),
            ft.ExpansionTile(
                title=ft.Text("ユーザー入力"),
                expanded=True,
                controls=[self._input_column, self._run_button],
            ),
            self._response_tile,
        ]

    def _on_config_changed(self, e: ft.ControlEvent) -> None:
        stem = self._config_dropdown.value
        if not stem or stem not in self._config_paths:
            return
        path = self._config_paths[stem]
        try:
            req = load_single_config(path)
        except Exception as ex:
            self._title_text.value = f"[ERROR] {ex}"
            self.update()
            return

        self._title_text.value = req.title
        self._note_text.value = req.note or ""

        n = count_user_inputs(req)
        self._input_column.controls = [
            ft.TextField(label=f"user_input_{i}", expand=True) for i in range(n)
        ]
        self._run_button.disabled = False
        self._response_text.value = ""
        self._raw_json_text.visible = False
        self.update()

    def _on_run(self, e: ft.ControlEvent) -> None:
        stem = self._config_dropdown.value
        if not stem:
            return
        path = self._config_paths[stem]
        user_inputs = [
            field.value or ""
            for field in self._input_column.controls
            if isinstance(field, ft.TextField)
        ]
        uc = make_single_usecase(self._store)
        try:
            result = uc.run(str(path), user_inputs=user_inputs, api_key=self._store.get_api_key())
        except Exception as ex:
            self._response_text.value = f"[ERROR] {ex}"
            self._response_text.color = ft.Colors.RED
            self._response_tile.expanded = True
            self.update()
            return

        if not result.is_success:
            self._response_text.value = f"[ERROR {result.status_code}] {result.error}"
            self._response_text.color = ft.Colors.RED
        else:
            display = result.extracted if result.extracted is not None else result.body
            self._response_text.value = str(display)
            self._response_text.color = ft.Colors.ON_SURFACE
            self._raw_json_text.value = json.dumps(result.body, ensure_ascii=False, indent=2)
            self._raw_json_text.visible = True

        self._response_tile.expanded = True
        self.update()
