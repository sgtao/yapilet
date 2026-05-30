from __future__ import annotations

import flet as ft
from yapilet.gui.app_store import AppStore


class SettingsPage(ft.Column):
    """Settings: API Key と mock_echo を設定する。変更は store に即時反映。"""

    def __init__(self, store: AppStore) -> None:
        super().__init__(scroll=ft.ScrollMode.AUTO, expand=True, spacing=16)
        self._store = store

        self._api_key_field = ft.TextField(
            label="API Key",
            value=store.api_key,
            password=True,
            can_reveal_password=True,
            expand=True,
            on_change=self._on_api_key_change,
        )
        self._mock_switch = ft.Switch(
            label="Mock Echo モード（実 HTTP を送らない）",
            value=store.mock_echo,
            on_change=self._on_mock_change,
        )

        self.controls = [
            ft.Text("Settings", size=20, weight=ft.FontWeight.BOLD),
            ft.Divider(),
            ft.Text("API Key", weight=ft.FontWeight.W_600),
            ft.Text(
                "API_KEY 環境変数が設定済みの場合は空白のままで OK",
                size=12,
                color=ft.Colors.GREY_500,
            ),
            ft.Row([self._api_key_field]),
            ft.Divider(),
            self._mock_switch,
            ft.Text(
                "Mock ON: 実 HTTP リクエストを送らず、リクエスト内容を echo して返す",
                size=12,
                color=ft.Colors.GREY_500,
            ),
        ]

    def _on_api_key_change(self, e: ft.Event[ft.TextField]) -> None:
        self._store.api_key = e.control.value or ""

    def _on_mock_change(self, e: ft.Event[ft.Switch]) -> None:
        self._store.mock_echo = bool(e.control.value)
