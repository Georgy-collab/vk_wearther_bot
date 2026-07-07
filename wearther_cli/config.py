"""Конфигурация приложения: загрузка переменных окружения."""

import os

from dotenv import load_dotenv

load_dotenv()

# API-ключ OpenWeatherMap читается из файла .env (переменная API_KEY).
API_KEY = os.getenv("API_KEY")
