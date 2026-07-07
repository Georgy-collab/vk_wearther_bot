"""Консольный интерфейс приложения погоды (точка входа)."""

from display import print_air_pollution, print_forecast, print_weather
from weather_service import get_air_pollution, get_current_weather, get_forecast


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


def main() -> None:
    """Запускает главный цикл меню: выбор действия, ввод места и вывод данных."""
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
                print_weather(weather)
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


if __name__ == "__main__":
    main()
