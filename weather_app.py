from collections import defaultdict

from dotenv import load_dotenv
import os
from http_client import get_request

load_dotenv()
API_KEY = os.getenv("API_KEY")

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
    "so2": ("SO₂", (20, 80, 250, 350)),
    "no2": ("NO₂", (40, 70, 150, 200)),
    "pm10": ("PM10", (20, 50, 100, 200)),
    "pm2_5": ("PM2.5", (10, 25, 50, 75)),
    "o3": ("O₃", (60, 100, 140, 180)),
    "co": ("CO", (4400, 9400, 12400, 15400)),
}


def get_coordinates(city: str) -> tuple[float, float] | None:
    """Определяет широту и долготу города через геокодер OpenWeatherMap.

    Возвращает кортеж (широта, долгота) или (None, None), если город
    не найден или запрос не удался.
    """
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={API_KEY}&limit=1&lang=ru"
    response = get_request(url)
    if response is None:
        return None, None
    data = response.json()
    if len(data) == 0:
        return None, None
    return data[0]["lat"], data[0]["lon"]


def resolve_coordinates(
    city: str = None, latitude: float = None, longitude: float = None
) -> tuple[float, float] | None:
    """Приводит место к координатам: по названию города или из переданных
    широты и долготы.

    Возвращает кортеж (широта, долгота) или (None, None) при ошибке;
    сообщение об ошибке выводится в консоль.
    """
    if city:
        latitude, longitude = get_coordinates(city)
        if latitude is None or longitude is None:
            print(f"Не удалось получить координаты города {city}")
            return None, None
        return latitude, longitude
    if latitude is not None and longitude is not None:
        return latitude, longitude
    print("Необходимо указать город или координаты")
    return None, None


def get_current_weather(
    city: str = None, latitude: float = None, longitude: float = None
) -> dict | None:
    """Возвращает текущую погоду по городу или координатам.

    Возвращает словарь ответа API или None, если данные получить не удалось.
    """
    latitude, longitude = resolve_coordinates(city, latitude, longitude)
    if latitude is None or longitude is None:
        return None
    return get_weather_by_coordinates(latitude, longitude)


def get_weather_by_coordinates(latitude: float, longitude: float) -> dict | None:
    """Запрашивает текущую погоду по координатам через Current Weather API.

    Возвращает словарь ответа API или None при ошибке запроса.
    """
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric&lang=ru"
    response = get_request(url)
    if response is None:
        return None
    data = response.json()
    return data


def get_forecast(
    city: str = None, latitude: float = None, longitude: float = None
) -> dict | None:
    """Возвращает прогноз погоды на 5 дней по городу или координатам.

    Возвращает словарь ответа API или None, если данные получить не удалось.
    """
    latitude, longitude = resolve_coordinates(city, latitude, longitude)
    if latitude is None or longitude is None:
        return None
    return get_forecast_by_coordinates(latitude, longitude)


def get_forecast_by_coordinates(latitude: float, longitude: float) -> dict | None:
    """Запрашивает прогноз на 5 дней (с шагом 3 часа) по координатам.

    Возвращает словарь ответа API или None при ошибке запроса.
    """
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric&lang=ru"
    response = get_request(url)
    if response is None:
        return None
    return response.json()


def get_air_pollution(
    city: str = None, latitude: float = None, longitude: float = None
) -> dict | None:
    """Возвращает данные о качестве воздуха по городу или координатам.

    Возвращает словарь ответа API или None, если данные получить не удалось.
    """
    latitude, longitude = resolve_coordinates(city, latitude, longitude)
    if latitude is None or longitude is None:
        return None
    return get_air_pollution_by_coordinates(latitude, longitude)


def get_air_pollution_by_coordinates(latitude: float, longitude: float) -> dict | None:
    """Запрашивает данные о качестве воздуха по координатам через Air Pollution API.

    Возвращает словарь ответа API или None при ошибке запроса.
    """
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={latitude}&lon={longitude}&appid={API_KEY}"
    response = get_request(url)
    if response is None:
        return None
    return response.json()


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


def pollutant_level(value: float, thresholds: tuple[float, ...]) -> int:
    """Возвращает уровень качества воздуха (1–5) для концентрации загрязнителя
    по верхним границам категорий из таблицы.
    """
    for index, upper in enumerate(thresholds):
        if value < upper:
            return index + 1
    return 5


def print_air_pollution(data: dict) -> None:
    """Печатает интерпретацию качества воздуха на русском языке: общий индекс
    и перечень загрязнителей, концентрация которых превышает норму
    (уровень выше «Хорошее»).
    """
    items = data.get("list", [])
    if not items:
        print("Нет данных о качестве воздуха.")
        return

    record = items[0]
    aqi = record["main"]["aqi"]
    components = record["components"]
    print(f"Качество воздуха: {AIR_QUALITY_LEVELS[aqi - 1]} (индекс {aqi})")

    exceeded = []
    for key, (label, thresholds) in POLLUTANT_THRESHOLDS.items():
        value = components.get(key)
        if value is None:
            continue
        level = pollutant_level(value, thresholds)
        if level > 1:
            exceeded.append((label, value, level))

    if exceeded:
        print("Превышены нормы по следующим загрязнителям:")
        for label, value, level in exceeded:
            print(f"  - {label}: {value} мкг/м³ — {AIR_QUALITY_LEVELS[level - 1]}")
    else:
        print("Все показатели в пределах нормы (уровень «Хорошее»).")


def ask_location() -> dict | None:
    """Спрашивает у пользователя способ указания места (город или координаты)
    и возвращает параметры для запроса в виде словаря.

    Возвращает None при некорректном вводе.
    """
    print("  1 — по городу")
    print("  2 — по координатам")
    sub_choice = input("Ваш выбор: ").strip()

    if sub_choice == "1":
        city = input("Введите название города: ").strip()
        return {"city": city}
    if sub_choice == "2":
        try:
            latitude = float(input("Введите широту: ").strip())
            longitude = float(input("Введите долготу: ").strip())
            return {"latitude": latitude, "longitude": longitude}
        except ValueError:
            print("Некорректный ввод координат.")
            return None
    print("Некорректный выбор.")
    return None


if __name__ == "__main__":
    while True:
        print("Что вы хотите сделать?")
        print("1 — Текущая погода")
        print("2 — Прогноз на 5 дней")
        print("3 — Качество воздуха")
        print("0 — Выход")
        choice = input("Ваш выбор: ").strip()

        if choice == "0":
            print("Выход из программы.")
            break

        if choice not in ("1", "2", "3"):
            print("Некорректный выбор. Попробуйте снова.")
            continue

        location = ask_location()
        if location is None:
            continue

        if choice == "1":
            weather = get_current_weather(**location)
            if weather:
                print(
                    f"Погода в {weather['name']}: {weather['main']['temp']}°C, "
                    f"{weather['weather'][0]['description']}"
                )
            else:
                print("Не удалось получить погоду")
        elif choice == "2":
            forecast = get_forecast(**location)
            if forecast:
                print_forecast(forecast)
            else:
                print("Не удалось получить прогноз")
        elif choice == "3":
            pollution = get_air_pollution(**location)
            if pollution:
                print_air_pollution(pollution)
            else:
                print("Не удалось получить данные о качестве воздуха")
