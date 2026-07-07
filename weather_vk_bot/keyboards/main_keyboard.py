"""Главное меню бота (нижняя клавиатура, не одноразовая).

Кнопки — типа Text с payload-командой: payload не виден пользователю и надёжно
маршрутизирует нажатие независимо от подписи/эмодзи.
"""

from __future__ import annotations

from vkbottle import Keyboard, KeyboardButtonColor, Text

# Команды меню (значение payload["cmd"]).
CMD_WEATHER = "weather"
CMD_FORECAST = "forecast"
CMD_GEO = "geo"
CMD_EXTENDED = "extended"
CMD_MY_CITY = "my_city"
CMD_COMPARE = "compare"
CMD_HELP = "help"


def main_menu() -> str:
    """JSON главного меню для параметра keyboard."""
    keyboard = (
        Keyboard(one_time=False, inline=False)
        .add(Text("🌤 Погода сейчас", payload={"cmd": CMD_WEATHER}),
             color=KeyboardButtonColor.PRIMARY)
        .add(Text("📅 Прогноз 5 дней", payload={"cmd": CMD_FORECAST}),
             color=KeyboardButtonColor.PRIMARY)
        .row()
        .add(Text("⭐ Мой город", payload={"cmd": CMD_MY_CITY}),
             color=KeyboardButtonColor.POSITIVE)
        .add(Text("⚖️ Сравнить города", payload={"cmd": CMD_COMPARE}),
             color=KeyboardButtonColor.POSITIVE)
        .row()
        .add(Text("📍 Геолокация", payload={"cmd": CMD_GEO}),
             color=KeyboardButtonColor.SECONDARY)
        .add(Text("🌫 Расширенный режим", payload={"cmd": CMD_EXTENDED}),
             color=KeyboardButtonColor.SECONDARY)
        .row()
        .add(Text("ℹ️ Помощь", payload={"cmd": CMD_HELP}),
             color=KeyboardButtonColor.SECONDARY)
    )
    return keyboard.get_json()
