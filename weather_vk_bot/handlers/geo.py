"""Сценарий геолокации.

Реализовано двумя способами (по реальным возможностям VK):
1. Нативная кнопка «Отправить местоположение» → в сообщении приходит
   ``message.geo`` с координатами.
2. Fallback: пользователь присылает координаты текстом
   ("55.7558, 37.6173" или "55.7558 37.6173").
"""

from __future__ import annotations

import logging

from vkbottle.bot import Message

from keyboards.main_keyboard import CMD_GEO, main_menu
from keyboards.navigation_keyboard import geo_request
from services.formatter import format_current
from services.parsing import parse_coordinates
from services.state_manager import WeatherStates

logger = logging.getLogger(__name__)

ASK_GEO = (
    "📍 Отправьте геолокацию кнопкой ниже\n"
    "──────────────\n"
    "или пришлите координаты текстом в формате:\n"
    "55.7558, 37.6173"
)
BAD_COORDS = (
    "⚠️ Не распознал координаты.\n"
    "Отправьте геолокацию кнопкой или пришлите их в формате:\n"
    "55.7558, 37.6173"
)


def register(bot, ctx) -> None:
    @bot.on.message(payload={"cmd": CMD_GEO})
    async def ask_geo(message: Message) -> None:
        await ctx.states.set(message.peer_id, WeatherStates.WAITING_GEO)
        await message.answer(ASK_GEO, keyboard=geo_request())


def register_states(bot, ctx) -> None:
    @bot.on.message(state=WeatherStates.WAITING_GEO)
    async def handle_geo(message: Message) -> None:
        coords = None
        if message.geo and message.geo.coordinates:
            coords = (message.geo.coordinates.latitude,
                      message.geo.coordinates.longitude)
        else:
            coords = parse_coordinates(message.text or "")

        if coords is None:
            await message.answer(BAD_COORDS, keyboard=geo_request())
            return

        lat, lon = coords
        try:
            data = await ctx.service.current_by_coordinates(lat, lon)
        except Exception:
            logger.exception("Ошибка погоды по координатам %s,%s", lat, lon)
            data = None

        if data is None:
            await message.answer(
                "❌ Не удалось получить погоду по этим координатам. "
                "Попробуйте ещё раз:",
                keyboard=geo_request(),
            )
            return

        await message.answer(format_current(data), keyboard=main_menu())
        await ctx.states.reset(message.peer_id)
