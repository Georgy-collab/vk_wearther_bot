"""Сценарий «Прогноз на 5 дней»."""

from __future__ import annotations

import logging

from vkbottle.bot import Message

from keyboards.main_keyboard import CMD_FORECAST, main_menu
from keyboards.navigation_keyboard import navigation
from services.formatter import format_forecast
from services.state_manager import WeatherStates

logger = logging.getLogger(__name__)

ASK_CITY = "📅 Введите город для прогноза на 5 дней:"
EMPTY_INPUT = "⚠️ Пустой запрос. Введите название города:"


def register(bot, ctx) -> None:
    @bot.on.message(payload={"cmd": CMD_FORECAST})
    async def ask_city(message: Message) -> None:
        await ctx.states.set(message.peer_id, WeatherStates.WAITING_FORECAST_CITY)
        await message.answer(ASK_CITY, keyboard=navigation())


def register_states(bot, ctx) -> None:
    @bot.on.message(state=WeatherStates.WAITING_FORECAST_CITY)
    async def forecast(message: Message) -> None:
        city = (message.text or "").strip()
        if not city:
            await message.answer(EMPTY_INPUT, keyboard=navigation())
            return
        try:
            data = await ctx.service.forecast_by_city(city)
        except Exception:
            logger.exception("Ошибка прогноза для %s", city)
            data = None
        if data is None:
            await message.answer(
                f"❌ Не удалось получить прогноз для «{city}».\n"
                "Проверьте название и попробуйте снова:",
                keyboard=navigation(),
            )
            return
        await message.answer(format_forecast(data), keyboard=main_menu())
        await ctx.states.reset(message.peer_id)
