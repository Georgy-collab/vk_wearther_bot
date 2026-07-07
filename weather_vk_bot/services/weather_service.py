"""Связующее звено между VK-обработчиками и backend OpenWeatherAPI.

Здесь синхронный клиент OpenWeatherAPI оборачивается в асинхронный интерфейс
(через ``asyncio.to_thread``), чтобы не блокировать событийный цикл vkbottle.
Слой отдаёт готовые к оформлению структуры данных, не занимаясь их выводом.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from OpenWeatherAPI import OpenWeatherAPI

logger = logging.getLogger(__name__)


@dataclass
class ExtendedWeather:
    """Пакет данных для расширенного режима: погода + качество воздуха."""

    weather: dict
    air: dict | None


class WeatherService:
    """Асинхронный фасад над OpenWeatherAPI для обработчиков бота."""

    def __init__(self, api: OpenWeatherAPI) -> None:
        self._api = api

    async def current_by_city(self, city: str) -> dict | None:
        return await asyncio.to_thread(self._api.get_weather_by_city, city)

    async def current_by_coordinates(self, lat: float, lon: float) -> dict | None:
        return await asyncio.to_thread(self._api.get_weather_by_coordinates, lat, lon)

    async def forecast_by_city(self, city: str) -> dict | None:
        return await asyncio.to_thread(self._api.get_forecast_by_city, city)

    async def extended_by_city(self, city: str) -> ExtendedWeather | None:
        """Расширенные данные по городу: погода и (по возможности) воздух."""
        coords = await asyncio.to_thread(self._api.get_coordinates, city)
        if coords is None:
            return None
        return await self._extended_by_coordinates(*coords)

    async def extended_by_coordinates(self, lat: float, lon: float) -> ExtendedWeather | None:
        return await self._extended_by_coordinates(lat, lon)

    async def _extended_by_coordinates(self, lat: float, lon: float) -> ExtendedWeather | None:
        weather = await asyncio.to_thread(self._api.get_weather_by_coordinates, lat, lon)
        if weather is None:
            return None
        air = await asyncio.to_thread(self._api.get_air_pollution_by_coordinates, lat, lon)
        return ExtendedWeather(weather=weather, air=air)
