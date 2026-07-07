"""Сценарии «Погода сейчас» и «Расширенный режим».

Если у пользователя сохранён город (⭐ Мой город), результат показывается сразу
для него; кнопка «🔎 Другой город» позволяет разово запросить другой город.
"""

from __future__ import annotations

import logging

from vkbottle.bot import Message

from keyboards.main_keyboard import CMD_EXTENDED, CMD_WEATHER
from keyboards.navigation_keyboard import (CMD_OTHER_EXTENDED, CMD_OTHER_WEATHER,
                                           navigation, result_menu)
from services.formatter import format_current, format_extended
from services.state_manager import WeatherStates

logger = logging.getLogger(__name__)

ASK_CITY = "🌤 Введите название города:"
ASK_EXTENDED_CITY = "🌫 Расширенный режим.\nВведите город для полного отчёта:"
EMPTY_INPUT = "⚠️ Пустой запрос. Введите название города:"


def _not_found(city: str) -> str:
    return (f"❌ Не удалось найти «{city}» или сервис недоступен.\n"
            "Проверьте название и попробуйте снова:")


def register(bot, ctx) -> None:
    """Входные точки: для запомненного города — сразу результат."""

    @bot.on.message(payload={"cmd": CMD_WEATHER})
    async def weather_entry(message: Message) -> None:
        saved = ctx.cities.get_city(message.from_id)
        if not saved:
            await ctx.states.set(message.peer_id, WeatherStates.WAITING_CITY)
            await message.answer(ASK_CITY, keyboard=navigation())
            return
        await _send_current(message, ctx, saved)

    @bot.on.message(payload={"cmd": CMD_EXTENDED})
    async def extended_entry(message: Message) -> None:
        saved = ctx.cities.get_city(message.from_id)
        if not saved:
            await ctx.states.set(message.peer_id, WeatherStates.WAITING_EXTENDED)
            await message.answer(ASK_EXTENDED_CITY, keyboard=navigation())
            return
        await _send_extended(message, ctx, saved)

    @bot.on.message(payload={"cmd": CMD_OTHER_WEATHER})
    async def other_weather(message: Message) -> None:
        await ctx.states.set(message.peer_id, WeatherStates.WAITING_CITY)
        await message.answer(ASK_CITY, keyboard=navigation())

    @bot.on.message(payload={"cmd": CMD_OTHER_EXTENDED})
    async def other_extended(message: Message) -> None:
        await ctx.states.set(message.peer_id, WeatherStates.WAITING_EXTENDED)
        await message.answer(ASK_EXTENDED_CITY, keyboard=navigation())


def register_states(bot, ctx) -> None:
    """Обработка ручного ввода города (разовый запрос)."""

    @bot.on.message(state=WeatherStates.WAITING_CITY)
    async def current_weather(message: Message) -> None:
        city = (message.text or "").strip()
        if not city:
            await message.answer(EMPTY_INPUT, keyboard=navigation())
            return
        await _send_current(message, ctx, city, ask_again=True)

    @bot.on.message(state=WeatherStates.WAITING_EXTENDED)
    async def extended_weather(message: Message) -> None:
        city = (message.text or "").strip()
        if not city:
            await message.answer(EMPTY_INPUT, keyboard=navigation())
            return
        await _send_extended(message, ctx, city, ask_again=True)


async def _send_current(message: Message, ctx, city: str, ask_again: bool = False) -> None:
    try:
        data = await ctx.service.current_by_city(city)
    except Exception:
        logger.exception("Ошибка получения погоды для %s", city)
        data = None
    if data is None:
        keyboard = navigation() if ask_again else result_menu(CMD_OTHER_WEATHER)
        await message.answer(_not_found(city), keyboard=keyboard)
        return
    await message.answer(format_current(data), keyboard=result_menu(CMD_OTHER_WEATHER))
    await ctx.states.reset(message.peer_id)


async def _send_extended(message: Message, ctx, city: str, ask_again: bool = False) -> None:
    try:
        bundle = await ctx.service.extended_by_city(city)
    except Exception:
        logger.exception("Ошибка расширенной погоды для %s", city)
        bundle = None
    if bundle is None:
        keyboard = navigation() if ask_again else result_menu(CMD_OTHER_EXTENDED)
        await message.answer(_not_found(city), keyboard=keyboard)
        return
    await message.answer(format_extended(bundle), keyboard=result_menu(CMD_OTHER_EXTENDED))
    await ctx.states.reset(message.peer_id)
