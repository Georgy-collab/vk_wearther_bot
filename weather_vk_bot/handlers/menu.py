"""Обработчики главного меню и навигации.

Регистрируется первым (команды «старт»/«домой»/«назад») и последним
(catch-all fallback), чтобы навигация имела приоритет над сценариями ввода.
"""

from __future__ import annotations

import logging

from vkbottle.bot import Message

from keyboards.main_keyboard import (CMD_COMPARE, CMD_EXTENDED, CMD_FORECAST,
                                     CMD_GEO, CMD_HELP, CMD_MY_CITY,
                                     CMD_WEATHER, main_menu)
from keyboards.navigation_keyboard import (CMD_BACK, CMD_CHANGE_CITY, CMD_HOME,
                                           CMD_OTHER_EXTENDED, CMD_OTHER_FORECAST,
                                           CMD_OTHER_WEATHER, CMD_REFRESH)
from services.state_manager import WeatherStates

logger = logging.getLogger(__name__)

GREETING = (
    "👋 Привет! Я погодный бот.\n"
    "──────────────\n"
    "Что я умею:\n"
    "🌤 Текущая погода и 📅 прогноз на 5 дней\n"
    "⭐ Запомнить ваш город и обновлять его одной кнопкой\n"
    "⚖️ Сравнивать погоду двух городов\n"
    "📍 Погода по геолокации\n"
    "🌫 Расширенный режим с качеством воздуха\n\n"
    "Выберите действие в меню ниже 👇"
)

MENU_HINT = "🏠 Главное меню. Выберите действие:"

START_WORDS = {"/start", "start", "начать", "старт", "привет", "здравствуйте",
               "меню", "menu", "hi", "hello", "старт бот", "start bot"}


def _is_start(message: Message) -> bool:
    """Совпадение со «стартом»: команда VK (payload command=start) или текст."""
    payload = message.get_payload_json() or {}
    if isinstance(payload, dict) and payload.get("command") == "start":
        return True
    return (message.text or "").strip().lower() in START_WORDS


async def show_main_menu(message: Message, ctx, text: str = MENU_HINT) -> None:
    """Показывает главное меню и сбрасывает состояние в MAIN_MENU."""
    await ctx.states.reset(message.peer_id)
    await message.answer(text, keyboard=main_menu())


ONBOARDING = (
    "💡 Совет: введите ваш город — я запомню его, и тогда «Погода сейчас», "
    "«Прогноз» и «Расширенный режим» будут показывать погоду для него одной "
    "кнопкой.\n\nИли просто выберите действие в меню 👇"
)


def register(bot, ctx) -> None:
    """Команды старта и навигации (высокий приоритет)."""

    @bot.on.message(func=_is_start)
    async def start_handler(message: Message) -> None:
        saved = ctx.cities.get_city(message.from_id)
        if saved:
            await ctx.states.reset(message.peer_id)
            await message.answer(
                GREETING + f"\n\n⭐ Ваш город: {saved}.",
                keyboard=main_menu(),
            )
            return
        # Онбординг: предлагаем запомнить город (текст сохранится как избранный).
        await ctx.states.set(message.peer_id, WeatherStates.WAITING_SAVE_CITY)
        await message.answer(GREETING + "\n\n" + ONBOARDING, keyboard=main_menu())

    @bot.on.message(payload={"cmd": CMD_HOME})
    async def home_handler(message: Message) -> None:
        await show_main_menu(message, ctx)

    @bot.on.message(payload={"cmd": CMD_BACK})
    async def back_handler(message: Message) -> None:
        await show_main_menu(message, ctx)


def register_fallback(bot, ctx) -> None:
    """Catch-all: должен регистрироваться последним из всех обработчиков."""

    known = {CMD_WEATHER, CMD_FORECAST, CMD_GEO, CMD_EXTENDED,
             CMD_MY_CITY, CMD_COMPARE, CMD_HELP, CMD_BACK, CMD_HOME,
             CMD_REFRESH, CMD_CHANGE_CITY, CMD_OTHER_WEATHER,
             CMD_OTHER_FORECAST, CMD_OTHER_EXTENDED}

    @bot.on.message()
    async def fallback_handler(message: Message) -> None:
        payload = message.get_payload_json() or {}
        if isinstance(payload, dict) and payload.get("cmd") in known:
            return
        await message.answer(
            "🤔 Не понял команду. Воспользуйтесь кнопками меню 👇",
            keyboard=main_menu(),
        )
