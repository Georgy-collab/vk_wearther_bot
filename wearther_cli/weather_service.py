"""Доступ к OpenWeatherMap API.

Все функции возвращают данные (словарь или кортеж) либо None при ошибке.
Вывод сообщений об ошибках остаётся на стороне вызывающего кода (CLI).
"""

from config import OPENWEATHER_API_KEY
from http_client import get_request


def get_coordinates(city: str) -> tuple[float, float] | None:
    """Определяет широту и долготу города через геокодер OpenWeatherMap.

    Возвращает кортеж (широта, долгота) или (None, None), если город
    не найден или запрос не удался.
    """
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={OPENWEATHER_API_KEY}&limit=1&lang=ru"
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

    Возвращает кортеж (широта, долгота) или (None, None) при ошибке.
    """
    if city:
        latitude, longitude = get_coordinates(city)
        if latitude is None or longitude is None:
            return None, None
        return latitude, longitude
    if latitude is not None and longitude is not None:
        return latitude, longitude
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
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
    response = get_request(url)
    if response is None:
        return None
    return response.json()


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
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
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
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={latitude}&lon={longitude}&appid={OPENWEATHER_API_KEY}"
    response = get_request(url)
    if response is None:
        return None
    return response.json()
