"""Сценарий «Прогноз на 5 дней».

Если сохранён город (⭐ Мой город) — прогноз показывается сразу для него;
кнопка «🔎 Другой город» позволяет разово запросить другой город.
"""

from __future__ import annotations

import logging

from vkbottle.bot import Message

from keyboards.main_keyboard import CMD_FORECAST
from keyboards.navigation_keyboard import (CMD_OTHER_FORECAST, navigation,
                                           result_menu)
from services.formatter import format_forecast
from services.state_manager import WeatherStates

logger = logging.getLogger(__name__)

ASK_CITY = "📅 Введите город для прогноза на 5 дней:"
EMPTY_INPUT = "⚠️ Пустой запрос. Введите название города:"


def register(bot, ctx) -> None:
    @bot.on.message(payload={"cmd": CMD_FORECAST})
    async def forecast_entry(message: Message) -> None:
        saved = ctx.cities.get_city(message.from_id)
        if not saved:
            await ctx.states.set(message.peer_id, WeatherStates.WAITING_FORECAST_CITY)
            await message.answer(ASK_CITY, keyboard=navigation())
            return
        await _send_forecast(message, ctx, saved)

    @bot.on.message(payload={"cmd": CMD_OTHER_FORECAST})
    async def other_forecast(message: Message) -> None:
        await ctx.states.set(message.peer_id, WeatherStates.WAITING_FORECAST_CITY)
        await message.answer(ASK_CITY, keyboard=navigation())


def register_states(bot, ctx) -> None:
    @bot.on.message(state=WeatherStates.WAITING_FORECAST_CITY)
    async def forecast(message: Message) -> None:
        city = (message.text or "").strip()
        if not city:
            await message.answer(EMPTY_INPUT, keyboard=navigation())
            return
        await _send_forecast(message, ctx, city, ask_again=True)


async def _send_forecast(message: Message, ctx, city: str, ask_again: bool = False) -> None:
    try:
        data = await ctx.service.forecast_by_city(city)
    except Exception:
        logger.exception("Ошибка прогноза для %s", city)
        data = None
    if data is None:
        keyboard = navigation() if ask_again else result_menu(CMD_OTHER_FORECAST)
        await message.answer(
            f"❌ Не удалось получить прогноз для «{city}».\n"
            "Проверьте название и попробуйте снова:",
            keyboard=keyboard,
        )
        return
    await message.answer(format_forecast(data), keyboard=result_menu(CMD_OTHER_FORECAST))
    await ctx.states.reset(message.peer_id)
