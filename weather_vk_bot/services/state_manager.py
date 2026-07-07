"""FSM: описание состояний и обёртка над StateDispenser vkbottle.

Логика состояний вынесена сюда, чтобы обработчики (handlers/) занимались
только пользовательскими сценариями, а не деталями хранения состояния.
"""

from __future__ import annotations

from vkbottle import BaseStateGroup
from vkbottle.dispatch.dispenser.base import StatePeer


class WeatherStates(BaseStateGroup):
    """Состояния диалога погодного бота."""

    MAIN_MENU = "main_menu"
    WAITING_CITY = "waiting_city"
    WAITING_FORECAST_CITY = "waiting_forecast_city"
    WAITING_GEO = "waiting_geo"
    WAITING_EXTENDED = "waiting_extended"


class StateManager:
    """Тонкая обёртка над BuiltinStateDispenser бота."""

    def __init__(self, dispenser) -> None:
        self._dispenser = dispenser

    async def set(self, peer_id: int, state: BaseStateGroup, **payload) -> None:
        await self._dispenser.set(peer_id, state, **payload)

    async def get(self, peer_id: int) -> StatePeer | None:
        return await self._dispenser.get(peer_id)

    async def reset(self, peer_id: int) -> None:
        """Возврат в главное меню (сброс сценария)."""
        await self._dispenser.set(peer_id, WeatherStates.MAIN_MENU)
