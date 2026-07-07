"""Backend-слой доступа к OpenWeatherMap API.

Модуль изолирован от VK и Telegram: он ничего не знает о боте и возвращает
"сырые" словари ответа OpenWeatherMap либо ``None`` при ошибке. Всю
интерпретацию и оформление делает вышестоящий слой (services/formatter.py).

Класс синхронный (использует ``requests``); в асинхронном коде бота вызовы
оборачиваются в поток через ``asyncio.to_thread`` (см. services/weather_service.py).
"""

from __future__ import annotations

import logging
import time

import requests

logger = logging.getLogger(__name__)

GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
AIR_URL = "http://api.openweathermap.org/data/2.5/air_pollution"

RETRY_DELAYS = (1, 2, 4)
MAX_RETRIES = len(RETRY_DELAYS)
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class OpenWeatherAPI:
    """Клиент OpenWeatherMap с повторными попытками и обработкой ошибок."""

    def __init__(self, api_key: str, *, lang: str = "ru", units: str = "metric",
                 timeout: int = 10) -> None:
        if not api_key:
            raise ValueError("Не задан ключ OpenWeatherMap (OPENWEATHER_API_KEY).")
        self.api_key = api_key
        self.lang = lang
        self.units = units
        self.timeout = timeout
        self._session = requests.Session()

    def _get(self, url: str, params: dict) -> dict | list | None:
        """GET-запрос с ретраями. Возвращает распарсенный JSON или None."""
        params = {**params, "appid": self.api_key}
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = self._session.get(url, params=params, timeout=self.timeout)
            except requests.RequestException as error:
                logger.warning("Сетевая ошибка (%s): %s", url, error)
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAYS[attempt])
                    continue
                return None

            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError as error:
                    logger.error("Некорректный JSON от %s: %s", url, error)
                    return None

            if response.status_code in RETRYABLE_STATUS and attempt < MAX_RETRIES:
                logger.info("Код %s от %s, повтор...", response.status_code, url)
                time.sleep(RETRY_DELAYS[attempt])
                continue

            logger.warning("Ошибка %s от %s: %s", response.status_code, url,
                           response.text[:200])
            return None
        return None

    def get_coordinates(self, city: str) -> tuple[float, float] | None:
        """Возвращает (широта, долгота) города или None, если не найден."""
        data = self._get(GEO_URL, {"q": city, "limit": 1, "lang": self.lang})
        if not data:
            return None
        return data[0]["lat"], data[0]["lon"]

    def get_weather_by_coordinates(self, lat: float, lon: float) -> dict | None:
        """Текущая погода по координатам."""
        return self._get(WEATHER_URL, {
            "lat": lat, "lon": lon, "units": self.units, "lang": self.lang,
        })

    def get_weather_by_city(self, city: str) -> dict | None:
        """Текущая погода по названию города (через геокодер)."""
        coords = self.get_coordinates(city)
        if coords is None:
            return None
        return self.get_weather_by_coordinates(*coords)

    def get_forecast_by_coordinates(self, lat: float, lon: float) -> dict | None:
        """Прогноз на 5 дней (шаг 3 часа) по координатам."""
        return self._get(FORECAST_URL, {
            "lat": lat, "lon": lon, "units": self.units, "lang": self.lang,
        })

    def get_forecast_by_city(self, city: str) -> dict | None:
        """Прогноз на 5 дней по названию города."""
        coords = self.get_coordinates(city)
        if coords is None:
            return None
        return self.get_forecast_by_coordinates(*coords)

    def get_air_pollution_by_coordinates(self, lat: float, lon: float) -> dict | None:
        """Данные о качестве воздуха по координатам."""
        return self._get(AIR_URL, {"lat": lat, "lon": lon})
