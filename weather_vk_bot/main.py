"""Точка входа VK Weather Bot.

Загружает переменные окружения (.env), настраивает логирование и запускает бота.
Запуск: ``python main.py`` (из папки weather_vk_bot).
"""

from __future__ import annotations

import logging
import os
import sys

from dotenv import load_dotenv

from bot import VKWeatherBot


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    # vkbottle шумит на уровне INFO — оставляем только предупреждения.
    logging.getLogger("vkbottle").setLevel(logging.WARNING)


def main() -> int:
    configure_logging()
    load_dotenv()

    vk_token = os.getenv("VK_BOT_TOKEN")
    openweather_key = os.getenv("OPENWEATHER_API_KEY")

    if not vk_token:
        logging.error("Не задан VK_BOT_TOKEN в .env")
        return 1
    if not openweather_key:
        logging.error("Не задан OPENWEATHER_API_KEY в .env")
        return 1

    try:
        VKWeatherBot(vk_token, openweather_key).run()
    except KeyboardInterrupt:
        logging.info("Остановка по Ctrl+C")
    except Exception:
        logging.exception("Критическая ошибка при работе бота")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
