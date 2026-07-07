"""Сценарий «Мой город»: сохранение избранного города и быстрый показ погоды.

Позволяет один раз указать город и затем получать погоду одной кнопкой
(«Обновить»), не вводя название каждый раз.
"""

from __future__ import annotations

import logging

from vkbottle.bot import Message

from keyboards.main_keyboard import CMD_MY_CITY
from keyboards.navigation_keyboard import (CMD_CHANGE_CITY, CMD_REFRESH,
                                           navigation, saved_city_menu)
from services.formatter import format_current
from services.state_manager import WeatherStates

logger = logging.getLogger(__name__)

ASK_SAVE_CITY = "⭐ Введите город, который я запомню:"
EMPTY_INPUT = "⚠️ Пустой запрос. Введите название города:"


def _not_found(city: str) -> str:
    return (f"❌ Не удалось найти «{city}» или сервис недоступен.\n"
            "Попробуйте другой город:")


async def _show_saved_weather(message: Message, ctx) -> None:
    """Показывает погоду сохранённого города или просит его задать."""
    city = ctx.cities.get_city(message.from_id)
    if not city:
        await ctx.states.set(message.peer_id, WeatherStates.WAITING_SAVE_CITY)
        await message.answer(
            "У вас пока нет сохранённого города.\n" + ASK_SAVE_CITY,
            keyboard=navigation(),
        )
        return
    try:
        data = await ctx.service.current_by_city(city)
    except Exception:
        logger.exception("Ошибка погоды сохранённого города %s", city)
        data = None
    if data is None:
        await message.answer(
            f"❌ Не удалось получить погоду для сохранённого города «{city}».",
            keyboard=saved_city_menu(),
        )
        return
    header = f"⭐ Ваш город\n{format_current(data)}"
    await message.answer(header, keyboard=saved_city_menu())
    await ctx.states.reset(message.peer_id)


def register(bot, ctx) -> None:
    @bot.on.message(payload={"cmd": CMD_MY_CITY})
    async def my_city(message: Message) -> None:
        await _show_saved_weather(message, ctx)

    @bot.on.message(payload={"cmd": CMD_REFRESH})
    async def refresh(message: Message) -> None:
        await _show_saved_weather(message, ctx)

    @bot.on.message(payload={"cmd": CMD_CHANGE_CITY})
    async def change_city(message: Message) -> None:
        await ctx.states.set(message.peer_id, WeatherStates.WAITING_SAVE_CITY)
        await message.answer(ASK_SAVE_CITY, keyboard=navigation())


def register_states(bot, ctx) -> None:
    @bot.on.message(state=WeatherStates.WAITING_SAVE_CITY)
    async def save_city(message: Message) -> None:
        city = (message.text or "").strip()
        if not city:
            await message.answer(EMPTY_INPUT, keyboard=navigation())
            return
        try:
            data = await ctx.service.current_by_city(city)
        except Exception:
            logger.exception("Ошибка проверки города %s", city)
            data = None
        if data is None:
            await message.answer(_not_found(city), keyboard=navigation())
            return
        # Сохраняем нормализованное имя города из ответа API.
        saved_name = data.get("name") or city
        ctx.cities.set_city(message.from_id, saved_name)
        header = f"✅ Город «{saved_name}» сохранён.\n{format_current(data)}"
        await message.answer(header, keyboard=saved_city_menu())
        await ctx.states.reset(message.peer_id)
