"""Оформление данных о погоде в красивые текстовые сообщения.

Слой занимается ТОЛЬКО форматированием: на вход — словари OpenWeatherMap,
на выход — готовые строки для отправки в VK. Никаких сетевых вызовов и логики
состояний здесь нет.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from .weather_service import ExtendedWeather

DIVIDER = "──────────────"

WEEKDAYS = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")

AIR_QUALITY_LEVELS = {
    1: "Отличное",
    2: "Хорошее",
    3: "Умеренное",
    4: "Плохое",
    5: "Очень плохое",
}

AIR_ADVICE = {
    1: "Воздух чистый — отличное время для прогулки.",
    2: "Качество воздуха хорошее, ограничений нет.",
    3: "Приемлемо, но чувствительным группам стоит сократить долгие нагрузки на улице.",
    4: "Качество воздуха плохое — по возможности сократите время на улице.",
    5: "Очень грязный воздух — избегайте длительного пребывания на улице.",
}

POLLUTANT_THRESHOLDS = {
    "pm2_5": ("PM2.5", (10, 25, 50, 75)),
    "pm10": ("PM10", (20, 50, 100, 200)),
    "no2": ("NO2", (40, 70, 150, 200)),
    "so2": ("SO2", (20, 80, 250, 350)),
    "o3": ("O3", (60, 100, 140, 180)),
    "co": ("CO", (4400, 9400, 12400, 15400)),
}


def _temp(value: float) -> str:
    """Температура со знаком: +21°C / -5°C / 0°C."""
    return f"{round(value):+d}°C".replace("+0°C", "0°C")


def _wind_direction(deg: float | None) -> str:
    if deg is None:
        return ""
    points = ("С", "СВ", "В", "ЮВ", "Ю", "ЮЗ", "З", "СЗ")
    return points[round(deg / 45) % 8]


def _format_time(unix_ts: int, tz_offset: int) -> str:
    tz = timezone(timedelta(seconds=tz_offset))
    return datetime.fromtimestamp(unix_ts, tz).strftime("%H:%M")


def format_current(data: dict) -> str:
    """Базовая карточка текущей погоды."""
    main = data.get("main", {})
    weather = (data.get("weather") or [{}])[0]
    wind = data.get("wind", {})
    city = data.get("name") or "—"
    description = (weather.get("description") or "").capitalize()

    lines = [
        f"🌍 Город: {city}",
        DIVIDER,
        f"🌡 Температура: {_temp(main.get('temp', 0))}"
        f" (ощущается {_temp(main.get('feels_like', main.get('temp', 0)))})",
        f"☁️ {description}" if description else "☁️ Нет описания",
        f"💧 Влажность: {main.get('humidity', '—')}%",
        f"💨 Ветер: {round(wind.get('speed', 0))} м/с {_wind_direction(wind.get('deg'))}".strip(),
        f"📈 Давление: {round(main.get('pressure', 0) * 0.750062)} мм рт. ст.",
    ]
    return "\n".join(lines)


def format_forecast(data: dict) -> str:
    """Прогноз на 5 дней: агрегируем 3-часовые срезы по дням."""
    city = data.get("city", {}).get("name", "—")
    days: dict[str, list[dict]] = defaultdict(list)
    for item in data.get("list", []):
        date = item["dt_txt"].split(" ")[0]
        days[date].append(item)

    lines = [f"📅 Прогноз на 5 дней — {city}", DIVIDER]
    for date, items in list(days.items())[:5]:
        temps = [i["main"]["temp"] for i in items]
        midday = min(items, key=lambda i: abs(int(i["dt_txt"][11:13]) - 12))
        description = (midday["weather"][0]["description"] or "").capitalize()
        weekday = WEEKDAYS[datetime.strptime(date, "%Y-%m-%d").weekday()]
        day_label = datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m")
        lines.append(
            f"{weekday} {day_label}: {_temp(min(temps))}…{_temp(max(temps))} · {description}"
        )
    return "\n".join(lines)


def _short_card(data: dict) -> tuple[str, float, int, float]:
    """Короткая сводка для сравнения: (строка, темп, влажность, ветер)."""
    main = data.get("main", {})
    weather = (data.get("weather") or [{}])[0]
    wind = data.get("wind", {})
    city = data.get("name") or "—"
    temp = main.get("temp", 0)
    humidity = main.get("humidity", 0)
    speed = wind.get("speed", 0)
    desc = (weather.get("description") or "").capitalize()
    line = f"🏙 {city}: {_temp(temp)}, {desc}"
    return line, temp, humidity, speed


def format_compare(data_a: dict, data_b: dict) -> str:
    """Сравнение текущей погоды двух городов."""
    line_a, temp_a, hum_a, wind_a = _short_card(data_a)
    line_b, temp_b, hum_b, wind_b = _short_card(data_b)
    name_a = data_a.get("name") or "город A"
    name_b = data_b.get("name") or "город B"

    diff = round(temp_a - temp_b)
    if diff > 0:
        verdict = f"🌡 Теплее в {name_a} на {abs(diff)}°C"
    elif diff < 0:
        verdict = f"🌡 Теплее в {name_b} на {abs(diff)}°C"
    else:
        verdict = "🌡 Температура одинаковая"

    return "\n".join([
        "⚖️ Сравнение городов",
        DIVIDER,
        line_a,
        line_b,
        DIVIDER,
        verdict,
        f"💧 Влажность: {hum_a}% / {hum_b}%",
        f"💨 Ветер: {round(wind_a)} / {round(wind_b)} м/с",
    ])


def _air_index(components: dict) -> tuple[str, list[str]]:
    """Возвращает (строка-AQI-подсказка, список превышенных загрязнителей)."""
    exceeded = []
    for key, (label, thresholds) in POLLUTANT_THRESHOLDS.items():
        value = components.get(key)
        if value is None:
            continue
        level = next((i + 1 for i, up in enumerate(thresholds) if value < up), 5)
        if level > 2:
            exceeded.append(f"{label} — {AIR_QUALITY_LEVELS[level].lower()} ({round(value)} мкг/м³)")
    return "", exceeded


def format_extended(bundle: ExtendedWeather) -> str:
    """Расширенная карточка: погода + рассвет/закат + качество воздуха."""
    data = bundle.weather
    tz_offset = data.get("timezone", 0)
    sys = data.get("sys", {})

    parts = [format_current(data), DIVIDER]

    if sys.get("sunrise") and sys.get("sunset"):
        parts.append(f"🌅 Рассвет: {_format_time(sys['sunrise'], tz_offset)}")
        parts.append(f"🌇 Закат: {_format_time(sys['sunset'], tz_offset)}")

    air = bundle.air
    if air and air.get("list"):
        record = air["list"][0]
        aqi = record["main"]["aqi"]
        components = record.get("components", {})
        parts.append(DIVIDER)
        parts.append(f"🌫 Воздух: {AIR_QUALITY_LEVELS.get(aqi, '—')} (AQI {aqi})")
        _, exceeded = _air_index(components)
        if exceeded:
            parts.append("📊 Повышены: " + "; ".join(exceeded))
        else:
            parts.append("📊 Загрязнители в норме")
        parts.append(f"💬 {AIR_ADVICE.get(aqi, '')}")
    else:
        parts.append(DIVIDER)
        parts.append("🌫 Данные о качестве воздуха недоступны")

    return "\n".join(parts)
