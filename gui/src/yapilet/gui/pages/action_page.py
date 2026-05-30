from __future__ import annotations

from pathlib import Path

import flet as ft
from yapilet.gui._di import (
    ActionChain,
    list_action_configs,
    load_action_config,
    make_action_usecase,
)
from yapilet.gui.app_store import AppStore


class ActionPage(ft.Column):
    """Action Chain: アクションチェーン設定を選んでステップごとに実行する。"""

    def __init__(self, store: AppStore) -> None:
        super().__init__(scroll=ft.ScrollMode.AUTO, expand=True, spacing=8)
        self._store = store
        self._chain: ActionChain | None = None  # _on_config_changed でキャッシュ

        configs = list_action_configs()
        self._config_paths = {p.stem: p for p in configs}

        self._config_dropdown = ft.Dropdown(
            label="Action Config ファイル",
            options=[ft.dropdown.Option(stem) for stem in self._config_paths],
            expand=True,
            on_select=self._on_config_changed,  # type: ignore[arg-type]
        )
        self._title_text = ft.Text("", size=14, weight=ft.FontWeight.W_600)
        self._note_text = ft.Text("", size=12, color=ft.Colors.GREY_600, selectable=True)
        self._steps_info = ft.Text("", size=12, color=ft.Colors.GREY_500)
        self._user_input_field = ft.TextField(
            label="user_input_0（全ステップ共通）",
            expand=True,
        )
        self._run_button = ft.ElevatedButton(
            "▶ Run All Steps",
            icon=ft.Icons.PLAY_ARROW,
            on_click=self._on_run,  # type: ignore[arg-type]
            disabled=True,
        )
        self._result_column = ft.Column([], spacing=4)
        self._result_tile = ft.ExpansionTile(
            title=ft.Text("実行結果"),
            expanded=False,
            controls=[self._result_column],
        )

        self.controls = [
            ft.Text("Action Chain", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Row([self._config_dropdown]),
            ft.ExpansionTile(
                title=ft.Text("設定内容"),
                expanded=False,
                controls=[self._title_text, self._note_text, self._steps_info],
            ),
            ft.ExpansionTile(
                title=ft.Text("ユーザー入力"),
                expanded=True,
                controls=[self._user_input_field, self._run_button],
            ),
            self._result_tile,
        ]

    def _on_config_changed(self, e: ft.ControlEvent) -> None:
        stem = self._config_dropdown.value
        if not stem or stem not in self._config_paths:
            return
        path = self._config_paths[stem]
        try:
            self._chain = load_action_config(path)
        except Exception as ex:
            self._title_text.value = f"[ERROR] {ex}"
            self.update()
            return

        self._title_text.value = self._chain.title
        self._note_text.value = self._chain.note or ""
        self._steps_info.value = f"{len(self._chain.steps)} ステップ"
        self._run_button.disabled = False
        self._result_column.controls = []
        self.update()

    def _on_run(self, e: ft.ControlEvent) -> None:
        if self._chain is None:
            return
        stem = self._config_dropdown.value
        if not stem:
            return
        path = self._config_paths[stem]
        user_input = self._user_input_field.value or ""
        uc = make_action_usecase(self._store)

        self._result_column.controls = []
        try:
            results = uc.run(
                str(path),
                user_inputs=[user_input],
                api_key=self._store.get_api_key(),
            )
        except Exception as ex:
            self._result_column.controls = [ft.Text(f"[ERROR] {ex}", color=ft.Colors.RED)]
            self._result_tile.expanded = True
            self.update()
            return

        for i, (step, result) in enumerate(zip(self._chain.steps, results, strict=True), start=1):
            stem_name = Path(step.config).stem
            if not result.is_success:
                row: ft.Control = ft.Text(
                    f"step {i} ({stem_name}): [ERROR {result.status_code}] {result.error}",
                    color=ft.Colors.RED,
                    selectable=True,
                )
            else:
                value = result.extracted if result.extracted is not None else result.body
                row = ft.Text(
                    f"step {i} ({stem_name}): {value}",
                    selectable=True,
                )
            self._result_column.controls.append(row)

        self._result_tile.expanded = True
        self.update()
