from __future__ import annotations

import flet as ft
from yapilet.gui._di import ExecuteChatUseCase, list_chat_configs, make_chat_usecase
from yapilet.gui.app_store import AppStore


class ChatPage(ft.Column):
    """Chat: messages 配列を持つ single_config YAML を使った対話型ページ。

    [Load] の挙動:
        make_chat_usecase(store) + uc.load(path) の 2 段で use case を毎回再生成する。
        → api_key は send() ごとにライブ反映（再 Load 不要）。
        → mock_echo は [Load] 時のみ反映（history は seed にリセット）。

    [Clear] の挙動:
        保持中インスタンスに対して uc.load(path) のみ呼ぶ（use case は再生成しない）。
        → アダプタは [Load] 時点のものを維持。history は seed にリセット。

    Chat ドロップダウン注意:
        singles/ に body.messages を持たない config が混在する。
        そのような config を選んだ場合は seed なしでセッション開始となる。
    """

    def __init__(self, store: AppStore) -> None:
        super().__init__(expand=True, spacing=0)
        self._store = store
        self._uc: ExecuteChatUseCase | None = None
        self._seed_count = 0

        configs = list_chat_configs()
        self._config_paths = {p.stem: p for p in configs}

        self._config_dropdown = ft.Dropdown(
            label="Chat Config（body.messages を持つ config を選ぶこと）",
            options=[ft.dropdown.Option(stem) for stem in self._config_paths],
            expand=True,
        )
        self._load_button = ft.ElevatedButton(
            "Load",
            icon=ft.Icons.UPLOAD_FILE,
            on_click=self._on_load,  # type: ignore[arg-type]
        )
        self._clear_button = ft.OutlinedButton(
            "Clear",
            icon=ft.Icons.REFRESH,
            on_click=self._on_clear,  # type: ignore[arg-type]
            disabled=True,
        )
        self._message_list = ft.ListView(expand=True, spacing=4, padding=8, auto_scroll=True)
        self._input_field = ft.TextField(
            hint_text="メッセージを入力...",
            expand=True,
            multiline=False,
            on_submit=self._on_send,  # type: ignore[arg-type]
            disabled=True,
        )
        self._send_button = ft.IconButton(
            icon=ft.Icons.SEND,
            on_click=self._on_send,  # type: ignore[arg-type]
            disabled=True,
        )

        self.controls = [
            ft.Container(
                content=ft.Row([self._config_dropdown, self._load_button, self._clear_button]),
                padding=ft.padding.Padding(left=8, top=8, right=8, bottom=8),
            ),
            ft.Divider(height=1),
            ft.Container(content=self._message_list, expand=True),
            ft.Divider(height=1),
            ft.Container(
                content=ft.Row([self._input_field, self._send_button]),
                padding=ft.padding.Padding(left=8, top=8, right=8, bottom=8),
            ),
        ]

    def _on_load(self, e: ft.ControlEvent) -> None:
        stem = self._config_dropdown.value
        if not stem or stem not in self._config_paths:
            self._add_system_msg("[Error] config を選択してください")
            return
        path = self._config_paths[stem]
        try:
            self._uc = make_chat_usecase(self._store)
            self._uc.load(str(path))
        except Exception as ex:
            self._add_system_msg(f"[Error] {ex}")
            return

        self._message_list.controls.clear()
        self._seed_count = len(self._uc.history)

        for msg in self._uc.history:
            self._message_list.controls.append(
                self._make_bubble(msg["role"], str(msg.get("content", "")), is_seed=True)
            )

        self._input_field.disabled = False
        self._send_button.disabled = False
        self._clear_button.disabled = False
        self.update()

    def _on_clear(self, e: ft.ControlEvent) -> None:
        if self._uc is None:
            return
        stem = self._config_dropdown.value
        if not stem or stem not in self._config_paths:
            return
        path = self._config_paths[stem]
        try:
            self._uc.load(str(path))  # 既存インスタンスに load() のみ
        except Exception as ex:
            self._add_system_msg(f"[Error] {ex}")
            return

        self._message_list.controls.clear()
        self._seed_count = len(self._uc.history)
        for msg in self._uc.history:
            self._message_list.controls.append(
                self._make_bubble(msg["role"], str(msg.get("content", "")), is_seed=True)
            )
        self.update()

    def _on_send(self, e: ft.ControlEvent) -> None:
        if self._uc is None:
            return
        user_input = self._input_field.value or ""
        if not user_input.strip():
            return

        self._input_field.value = ""
        self._message_list.controls.append(self._make_bubble("user", user_input))
        self.update()

        try:
            response = self._uc.send(user_input, api_key=self._store.get_api_key())
        except Exception as ex:
            self._add_system_msg(f"[Error] {ex}")
            return

        if response is None:
            self._add_system_msg("[Error] リクエストが失敗しました")
        else:
            self._message_list.controls.append(self._make_bubble("assistant", response))
        self.update()

    def _add_system_msg(self, text: str) -> None:
        self._message_list.controls.append(
            ft.Container(
                content=ft.Text(text, color=ft.Colors.RED, size=12),
                padding=4,
            )
        )
        self.update()

    def _make_bubble(self, role: str, content: str, is_seed: bool = False) -> ft.Control:
        if is_seed:
            return ft.Container(
                content=ft.Text(
                    f"[{role}] {content}",
                    color=ft.Colors.GREY_500,
                    size=12,
                    italic=True,
                    selectable=True,
                ),
                padding=ft.padding.Padding(left=8, top=2, right=8, bottom=2),
            )
        if role == "user":
            return ft.Row(
                [
                    ft.Container(
                        content=ft.Text(content, selectable=True),
                        bgcolor=ft.Colors.BLUE_100,
                        border_radius=12,
                        padding=10,
                        margin=ft.margin.Margin(left=80, top=0, right=0, bottom=0),
                    )
                ],
                alignment=ft.MainAxisAlignment.END,
            )
        return ft.Row(
            [
                ft.Container(
                    content=ft.Text(content, selectable=True),
                    bgcolor=ft.Colors.GREY_200,
                    border_radius=12,
                    padding=10,
                    margin=ft.margin.Margin(left=0, top=0, right=80, bottom=0),
                )
            ],
            alignment=ft.MainAxisAlignment.START,
        )
