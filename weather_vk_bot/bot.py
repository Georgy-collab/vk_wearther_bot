"""Ядро приложения: сборка и запуск VK Weather Bot на VKBottle (Long Poll).

Класс ``VKWeatherBot`` инкапсулирует создание Bot, backend-клиента, сервисов и
регистрацию обработчиков. Модуль спроектирован под дальнейшее расширение
(подписки, уведомления, избранные города): достаточно добавить новый сервис в
``BotContext`` и новый обработчик в список ``_HANDLERS``.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from vkbottle import BaseMiddleware
from vkbottle.bot import Bot, Message

from handlers import forecast, geo, help as help_handler, menu, weather
from OpenWeatherAPI import OpenWeatherAPI
from services.state_manager import StateManager
from services.weather_service import WeatherService

logger = logging.getLogger(__name__)

# Обработчики с двухфазной регистрацией: сначала входные точки (кнопки/команды),
# затем состояния — чтобы навигация всегда имела приоритет над вводом города.
_HANDLERS = (menu, help_handler, weather, forecast, geo)


@dataclass
class BotContext:
    """Общие зависимости, передаваемые во все обработчики."""

    service: WeatherService
    states: StateManager


class LoggingMiddleware(BaseMiddleware[Message]):
    """Логирует входящие сообщения."""

    async def pre(self) -> None:
        text = (self.event.text or "").replace("\n", " ")[:100]
        logger.info("Входящее от id%s: %r", self.event.from_id, text)


class VKWeatherBot:
    """Погодный VK-бот: главный класс приложения."""

    def __init__(self, vk_token: str, openweather_key: str) -> None:
        self.bot = Bot(token=vk_token)
        self.context = BotContext(
            service=WeatherService(OpenWeatherAPI(openweather_key)),
            states=StateManager(self.bot.state_dispenser),
        )
        self._setup_middlewares()
        self._register_handlers()

    def _setup_middlewares(self) -> None:
        self.bot.labeler.message_view.register_middleware(LoggingMiddleware)

    def _register_handlers(self) -> None:
        # Фаза 1: входные точки (команды и кнопки меню).
        for module in _HANDLERS:
            module.register(self.bot, self.context)
        # Фаза 2: обработчики состояний FSM.
        for module in _HANDLERS:
            if hasattr(module, "register_states"):
                module.register_states(self.bot, self.context)
        # Фаза 3: catch-all — строго последним.
        menu.register_fallback(self.bot, self.context)
        logger.info("Обработчики зарегистрированы")

    def run(self) -> None:
        """Запускает Long Poll (блокирующий вызов)."""
        logger.info("Запуск бота (Long Poll)...")
        self.bot.run_forever()
