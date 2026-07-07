"""Навигационные клавиатуры: «Назад» / «Главное меню» и запрос геолокации."""

from __future__ import annotations

from vkbottle import Keyboard, KeyboardButtonColor, Location, Text

CMD_BACK = "back"
CMD_HOME = "home"
CMD_GEO_SHARE = "geo_share"
CMD_REFRESH = "refresh"
CMD_CHANGE_CITY = "change_city"
CMD_OTHER_WEATHER = "other_weather"
CMD_OTHER_FORECAST = "other_forecast"
CMD_OTHER_EXTENDED = "other_extended"


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


def result_menu(other_cmd: str) -> str:
    """Клавиатура под результатом для запомненного города.

    ``other_cmd`` — команда для запроса погоды по другому городу (разово).
    """
    keyboard = (
        Keyboard(one_time=False, inline=False)
        .add(Text("🔎 Другой город", payload={"cmd": other_cmd}),
             color=KeyboardButtonColor.SECONDARY)
        .row()
        .add(Text("🏠 Главное меню", payload={"cmd": CMD_HOME}),
             color=KeyboardButtonColor.POSITIVE)
    )
    return keyboard.get_json()


def saved_city_menu() -> str:
    """Клавиатура карточки сохранённого города: обновить / изменить / домой."""
    keyboard = (
        Keyboard(one_time=False, inline=False)
        .add(Text("🔄 Обновить", payload={"cmd": CMD_REFRESH}),
             color=KeyboardButtonColor.PRIMARY)
        .row()
        .add(Text("✏️ Изменить город", payload={"cmd": CMD_CHANGE_CITY}),
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
