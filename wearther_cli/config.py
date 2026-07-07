"""Конфигурация приложения: загрузка переменных окружения."""

import os

from dotenv import load_dotenv

load_dotenv()

# API-ключ OpenWeatherMap читается из файла .env (переменная OPENWEATHER_API_KEY).
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
