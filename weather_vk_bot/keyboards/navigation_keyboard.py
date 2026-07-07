"""Навигационные клавиатуры: «Назад» / «Главное меню» и запрос геолокации."""

from __future__ import annotations

from vkbottle import Keyboard, KeyboardButtonColor, Location, Text

CMD_BACK = "back"
CMD_HOME = "home"
CMD_GEO_SHARE = "geo_share"


def navigation() -> str:
    """Клавиатура навигации для сценариев ожидания ввода."""
    keyboard = (
        Keyboard(one_time=False, inline=False)
        .add(Text("⬅️ Назад", payload={"cmd": CMD_BACK}),
             color=KeyboardButtonColor.SECONDARY)
        .add(Text("🏠 Главное меню", payload={"cmd": CMD_HOME}),
             color=KeyboardButtonColor.POSITIVE)
    )
    return keyboard.get_json()


def geo_request() -> str:
    """Клавиатура для сценария геолокации: кнопка «отправить местоположение»."""
    keyboard = (
        Keyboard(one_time=False, inline=False)
        .add(Location(payload={"cmd": CMD_GEO_SHARE}))
        .row()
        .add(Text("⬅️ Назад", payload={"cmd": CMD_BACK}),
             color=KeyboardButtonColor.SECONDARY)
        .add(Text("🏠 Главное меню", payload={"cmd": CMD_HOME}),
             color=KeyboardButtonColor.POSITIVE)
    )
    return keyboard.get_json()
