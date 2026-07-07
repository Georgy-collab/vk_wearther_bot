from dotenv import load_dotenv
import os
from http_client import get_request

load_dotenv()
API_KEY = os.getenv("API_KEY")

def get_current_weather(city : str = None, latitude: float = None, longitude: float = None) -> dict | None:
    if city:
        latitude, longitude = get_coordinates(city)
        if latitude is None or longitude is None:
            print(f"Не удалось получить координаты города {city}")
            return None
        return get_weather_by_coordinates(latitude, longitude)
    elif latitude and longitude:
        return get_weather_by_coordinates(latitude, longitude)
    else:
        print("Необходимо указать город или координаты")
        return None

def get_coordinates(city: str) -> tuple[float, float] | None:
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&appid={API_KEY}&limit=1&lang=ru"
    response = get_request(url)
    if response is None:
        return None, None
    data = response.json()
    if len(data) == 0:
        return None, None
    return data[0]["lat"], data[0]["lon"]

def get_weather_by_coordinates(latitude: float, longitude: float) -> dict | None:
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={latitude}&lon={longitude}&appid={API_KEY}&units=metric&lang=ru"
    response = get_request(url)
    if response is None:
        return None
    data = response.json()
    return data

if __name__ == "__main__":
    while True:
        print("Что вы хотите сделать?")
        print("1 — Узнать погоду по городу")
        print("2 — Узнать погоду по координатам")
        print("0 — Выход")
        choice = input("Ваш выбор: ").strip()

        if choice == "1":
            city = input("Введите название города: ").strip()
            weather = get_current_weather(city=city)
            if weather:
                print(f"Погода в {city}: {weather['main']['temp']}°C, {weather['weather'][0]['description']}")
            else:
                print("Не удалось получить погоду")
        elif choice == "2":
            try:
                lat = float(input("Введите широту: ").strip())
                lon = float(input("Введите долготу: ").strip())
                weather = get_current_weather(latitude=lat, longitude=lon)
                if weather:
                    print(f"Погода на координатах {lat}, {lon}: {weather['main']['temp']}°C, {weather['weather'][0]['description']}")
                else:
                    print("Не удалось получить погоду")
            except ValueError:
                print("Некорректный ввод координат.")
        elif choice == "0":
            print("Выход из программы.")
            break
        else:
            print("Некорректный выбор. Попробуйте снова.")