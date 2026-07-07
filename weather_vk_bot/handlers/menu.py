"""Обработчики главного меню и навигации.

Регистрируется первым (команды «старт»/«домой»/«назад») и последним
(catch-all fallback), чтобы навигация имела приоритет над сценариями ввода.
"""

from __future__ import annotations

import logging

from vkbottle.bot import Message

from keyboards.main_keyboard import (CMD_EXTENDED, CMD_FORECAST, CMD_GEO,
                                     CMD_HELP, CMD_WEATHER, main_menu)
from keyboards.navigation_keyboard import CMD_BACK, CMD_HOME

logger = logging.getLogger(__name__)

GREETING = (
    "👋 Привет! Я погодный бот.\n"
    "──────────────\n"
    "Я умею показывать текущую погоду, прогноз на 5 дней, качество воздуха "
    "и работать с геолокацией.\n\n"
    "Выберите действие в меню ниже 👇"
)

MENU_HINT = "🏠 Главное меню. Выберите действие:"


async def show_main_menu(message: Message, ctx, text: str = MENU_HINT) -> None:
    """Показывает главное меню и сбрасывает состояние в MAIN_MENU."""
    await ctx.states.reset(message.peer_id)
    await message.answer(text, keyboard=main_menu())


def register(bot, ctx) -> None:
    """Команды старта и навигации (высокий приоритет)."""

    @bot.on.message(text=["/start", "start", "начать", "старт", "привет",
                          "меню", "menu"])
    async def start_handler(message: Message) -> None:
        await show_main_menu(message, ctx, GREETING)

    @bot.on.message(payload={"cmd": CMD_HOME})
    async def home_handler(message: Message) -> None:
        await show_main_menu(message, ctx)

    @bot.on.message(payload={"cmd": CMD_BACK})
    async def back_handler(message: Message) -> None:
        await show_main_menu(message, ctx)


def register_fallback(bot, ctx) -> None:
    """Catch-all: должен регистрироваться последним из всех обработчиков."""

    known = {CMD_WEATHER, CMD_FORECAST, CMD_GEO, CMD_EXTENDED, CMD_HELP,
             CMD_BACK, CMD_HOME}

    @bot.on.message()
    async def fallback_handler(message: Message) -> None:
        payload = message.get_payload_json() or {}
        if isinstance(payload, dict) and payload.get("cmd") in known:
            return
        await message.answer(
            "🤔 Не понял команду. Воспользуйтесь кнопками меню 👇",
            keyboard=main_menu(),
        )
