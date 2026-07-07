"""Интерпретация качества воздуха по таблице уровней OpenWeatherMap."""

# Русские названия уровней качества воздуха (индексы 1–5).
AIR_QUALITY_LEVELS = (
    "Хорошее",
    "Удовлетворительное",
    "Умеренное",
    "Плохое",
    "Очень плохое",
)

# Границы категорий из таблицы (в мкг/м³). Для каждого загрязнителя указаны
# верхние границы уровней 1–4; концентрация выше последней границы — уровень 5.
POLLUTANT_THRESHOLDS = {
    "so2": ("SO2", (20, 80, 250, 350)),
    "no2": ("NO2", (40, 70, 150, 200)),
    "pm10": ("PM10", (20, 50, 100, 200)),
    "pm2_5": ("PM2.5", (10, 25, 50, 75)),
    "o3": ("O3", (60, 100, 140, 180)),
    "co": ("CO", (4400, 9400, 12400, 15400)),
}


def pollutant_level(value: float, thresholds: tuple[float, ...]) -> int:
    """Возвращает уровень качества воздуха (1–5) для концентрации загрязнителя
    по верхним границам категорий из таблицы.
    """
    for index, upper in enumerate(thresholds):
        if value < upper:
            return index + 1
    return 5


def interpret_air_pollution(data: dict) -> dict | None:
    """Разбирает ответ Air Pollution API и возвращает интерпретацию.

    Возвращает словарь вида {"aqi": индекс, "exceeded": [(метка, значение,
    уровень), ...]}, где exceeded — загрязнители выше уровня «Хорошее».
    Возвращает None, если данных нет.
    """
    items = data.get("list", [])
    if not items:
        return None

    record = items[0]
    aqi = record["main"]["aqi"]
    components = record["components"]

    exceeded = []
    for key, (label, thresholds) in POLLUTANT_THRESHOLDS.items():
        value = components.get(key)
        if value is None:
            continue
        level = pollutant_level(value, thresholds)
        if level > 1:
            exceeded.append((label, value, level))

    return {"aqi": aqi, "exceeded": exceeded}
