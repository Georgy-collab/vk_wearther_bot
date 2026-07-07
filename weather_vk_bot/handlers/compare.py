"""Сценарий «Сравнить города»: погода двух городов рядом."""

from __future__ import annotations

import logging

from vkbottle.bot import Message

from keyboards.main_keyboard import CMD_COMPARE, main_menu
from keyboards.navigation_keyboard import navigation
from services.formatter import format_compare
from services.parsing import parse_two_cities
from services.state_manager import WeatherStates

logger = logging.getLogger(__name__)

ASK_CITIES = (
    "⚖️ Введите два города через запятую:\n"
    "Москва, Санкт-Петербург"
)
BAD_INPUT = "⚠️ Нужно ровно два города через запятую. Пример:\nМосква, Сочи"


def register(bot, ctx) -> None:
    @bot.on.message(payload={"cmd": CMD_COMPARE})
    async def ask_cities(message: Message) -> None:
        await ctx.states.set(message.peer_id, WeatherStates.WAITING_COMPARE)
        await message.answer(ASK_CITIES, keyboard=navigation())


def register_states(bot, ctx) -> None:
    @bot.on.message(state=WeatherStates.WAITING_COMPARE)
    async def compare(message: Message) -> None:
        cities = parse_two_cities(message.text or "")
        if cities is None:
            await message.answer(BAD_INPUT, keyboard=navigation())
            return
        city_a, city_b = cities
        try:
            data_a, data_b = await ctx.service.compare_cities(city_a, city_b)
        except Exception:
            logger.exception("Ошибка сравнения %s / %s", city_a, city_b)
            data_a = data_b = None

        missing = [c for c, d in ((city_a, data_a), (city_b, data_b)) if d is None]
        if missing:
            await message.answer(
                "❌ Не удалось найти: " + ", ".join(f"«{c}»" for c in missing)
                + ".\nПроверьте названия и попробуйте снова:",
                keyboard=navigation(),
            )
            return

        await message.answer(format_compare(data_a, data_b), keyboard=main_menu())
        await ctx.states.reset(message.peer_id)
