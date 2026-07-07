"""Сценарий «Помощь»."""

from __future__ import annotations

from vkbottle.bot import Message

from keyboards.main_keyboard import CMD_HELP, main_menu

HELP_TEXT = (
    "ℹ️ Возможности бота\n"
    "──────────────\n"
    "🌤 Погода сейчас — текущая погода по названию города\n"
    "📅 Прогноз 5 дней — прогноз с шагом по дням\n"
    "⭐ Мой город — запомнить город и смотреть погоду одной кнопкой «Обновить»\n"
    "⚖️ Сравнить города — погода двух городов рядом\n"
    "📍 Геолокация — погода по местоположению или координатам\n"
    "🌫 Расширенный режим — погода + рассвет/закат + качество воздуха\n"
    "──────────────\n"
    "Навигация: ⬅️ Назад и 🏠 Главное меню доступны в любой момент.\n"
    "Команда «Начать» или /start — перезапустить бота."
)


def register(bot, ctx) -> None:
    @bot.on.message(payload={"cmd": CMD_HELP})
    async def help_handler(message: Message) -> None:
        await message.answer(HELP_TEXT, keyboard=main_menu())
