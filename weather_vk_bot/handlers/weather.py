"""Сценарии «Погода сейчас» и «Расширенный режим»."""

from __future__ import annotations

import logging

from vkbottle.bot import Message

from keyboards.main_keyboard import CMD_EXTENDED, CMD_WEATHER, main_menu
from keyboards.navigation_keyboard import navigation
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
    """Входные точки сценариев (нажатие кнопок меню)."""

    @bot.on.message(payload={"cmd": CMD_WEATHER})
    async def ask_city(message: Message) -> None:
        await ctx.states.set(message.peer_id, WeatherStates.WAITING_CITY)
        await message.answer(ASK_CITY, keyboard=navigation())

    @bot.on.message(payload={"cmd": CMD_EXTENDED})
    async def ask_extended_city(message: Message) -> None:
        await ctx.states.set(message.peer_id, WeatherStates.WAITING_EXTENDED)
        await message.answer(ASK_EXTENDED_CITY, keyboard=navigation())


def register_states(bot, ctx) -> None:
    """Обработка ввода города в соответствующих состояниях."""

    @bot.on.message(state=WeatherStates.WAITING_CITY)
    async def current_weather(message: Message) -> None:
        city = (message.text or "").strip()
        if not city:
            await message.answer(EMPTY_INPUT, keyboard=navigation())
            return
        try:
            data = await ctx.service.current_by_city(city)
        except Exception:
            logger.exception("Ошибка получения погоды для %s", city)
            data = None
        if data is None:
            await message.answer(_not_found(city), keyboard=navigation())
            return
        await message.answer(format_current(data), keyboard=main_menu())
        await ctx.states.reset(message.peer_id)

    @bot.on.message(state=WeatherStates.WAITING_EXTENDED)
    async def extended_weather(message: Message) -> None:
        city = (message.text or "").strip()
        if not city:
            await message.answer(EMPTY_INPUT, keyboard=navigation())
            return
        try:
            bundle = await ctx.service.extended_by_city(city)
        except Exception:
            logger.exception("Ошибка расширенной погоды для %s", city)
            bundle = None
        if bundle is None:
            await message.answer(_not_found(city), keyboard=navigation())
            return
        await message.answer(format_extended(bundle), keyboard=main_menu())
        await ctx.states.reset(message.peer_id)
