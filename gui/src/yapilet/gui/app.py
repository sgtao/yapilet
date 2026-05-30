from __future__ import annotations

from typing import cast

import flet as ft
from yapilet.gui.app_store import AppStore
from yapilet.gui.pages.action_page import ActionPage
from yapilet.gui.pages.chat_page import ChatPage
from yapilet.gui.pages.settings_page import SettingsPage
from yapilet.gui.pages.single_page import SinglePage


def main(page: ft.Page) -> None:
    page.title = "yapilet"
    page.window.width = 800
    page.window.height = 700
    page.padding = 16

    store = AppStore()

    pages: list[ft.Control] = [
        SinglePage(store),  # Task 4
        ChatPage(store),  # Task 6
        ActionPage(store),  # Task 5
        SettingsPage(store),
    ]
    nav_labels = ["📝 Single", "💬 Chat", "🏃 Action", "⚙️ Settings"]

    content_ref: ft.Ref[ft.Container] = ft.Ref()
    nav_btn_refs: list[ft.Ref[ft.TextButton]] = [ft.Ref() for _ in nav_labels]

    def nav_to(idx: int) -> None:
        container = cast(ft.Container, content_ref.current)
        container.content = pages[idx]
        for i, ref in enumerate(nav_btn_refs):
            btn = cast(ft.TextButton, ref.current)
            btn.style = ft.ButtonStyle(
                color=ft.Colors.PRIMARY if i == idx else ft.Colors.ON_SURFACE_VARIANT
            )
        page.update()

    nav_buttons: list[ft.Control] = [
        ft.TextButton(
            label,
            ref=nav_btn_refs[i],
            on_click=lambda e, i=i: nav_to(i),
            style=ft.ButtonStyle(
                color=ft.Colors.PRIMARY if i == 0 else ft.Colors.ON_SURFACE_VARIANT
            ),
        )
        for i, label in enumerate(nav_labels)
    ]

    nav_bar = ft.Container(
        content=ft.Row(nav_buttons, alignment=ft.MainAxisAlignment.START),
        bgcolor=ft.Colors.SURFACE_VARIANT,
        padding=ft.padding.Padding(left=8, top=4, right=8, bottom=4),
        border_radius=ft.border_radius.BorderRadius(
            top_left=8, top_right=8, bottom_left=0, bottom_right=0
        ),
    )

    page.add(
        ft.Container(ref=content_ref, content=pages[0], expand=True),
        nav_bar,
    )


def main_entry() -> None:
    ft.app(target=main)  # type: ignore[no-untyped-call]


if __name__ == "__main__":
    main_entry()
