"""Форматирование и вывод данных в консоль."""

from collections import defaultdict

from air_quality import AIR_QUALITY_LEVELS, interpret_air_pollution


def print_weather(data: dict) -> None:
    """Печатает текущую погоду: город, температуру и описание."""
    print(
        f"Погода в {data['name']}: {data['main']['temp']}°C, "
        f"{data['weather'][0]['description']}"
    )


def print_forecast(data: dict) -> None:
    """Группирует прогноз по дням и печатает минимальную и максимальную
    температуру, а также описание погоды на середину дня.
    """
    city_name = data.get("city", {}).get("name", "")
    print(f"Прогноз на 5 дней для {city_name}:")

    days = defaultdict(list)
    for item in data.get("list", []):
        date = item["dt_txt"].split(" ")[0]
        days[date].append(item)

    for date, items in list(days.items())[:5]:
        temps = [item["main"]["temp"] for item in items]
        temp_min = min(temps)
        temp_max = max(temps)
        midday = min(items, key=lambda item: abs(int(item["dt_txt"][11:13]) - 12))
        description = midday["weather"][0]["description"]
        print(f"  {date}: от {temp_min:.0f}°C до {temp_max:.0f}°C, {description}")


def print_air_pollution(data: dict) -> None:
    """Печатает интерпретацию качества воздуха на русском языке: общий индекс
    и перечень загрязнителей, концентрация которых превышает норму
    (уровень выше «Хорошее»).
    """
    result = interpret_air_pollution(data)
    if result is None:
        print("Нет данных о качестве воздуха.")
        return

    aqi = result["aqi"]
    exceeded = result["exceeded"]
    print(f"Качество воздуха: {AIR_QUALITY_LEVELS[aqi - 1]} (индекс {aqi})")

    if exceeded:
        print("Превышены нормы по следующим загрязнителям:")
        for label, value, level in exceeded:
            print(f"  - {label}: {value} мкг/м3 — {AIR_QUALITY_LEVELS[level - 1]}")
    else:
        print("Все показатели в пределах нормы (уровень «Хорошее»).")
