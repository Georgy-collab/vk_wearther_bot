# OpenWeather CLI

Консольное приложение на Python для получения текущей погоды через [OpenWeatherMap API](https://openweathermap.org/api): по названию города или по координатам.

## Возможности

- Погода по городу (геокодирование + Current Weather API)
- Погода по широте и долготе
- Повторы запросов при 429 и временных сетевых ошибках (паузы 1 с, 2 с, 4 с)
- Обработка HTTP-ошибок и таймаутов

## Требования

- Python 3.10+
- API-ключ OpenWeatherMap (бесплатный тариф)

## Установка

```bash
git clone https://github.com/<ваш-логин>/<имя-репозитория>.git
cd <имя-репозитория>

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

pip install -r requirements.txt
```

Создайте файл `.env` по образцу `env.example.txt`:

```env
API_KEY=ваш_ключ_openweathermap
```

Ключ: [home.openweathermap.org/api_keys](https://home.openweathermap.org/api_keys)

## Запуск

```bash
python weather_app.py
```

Меню:

| Пункт | Действие |
|-------|----------|
| `1` | Погода по городу |
| `2` | Погода по координатам |
| `0` | Выход |

## Структура проекта

```
├── weather_app.py    # CLI и запросы к OpenWeatherMap
├── http_client.py    # GET/POST, обработка ошибок, retry
├── env.example.txt   # Шаблон переменных окружения
└── requirements.txt
```

## Зависимости

- `requests` — HTTP-запросы
- `python-dotenv` — загрузка `API_KEY` из `.env`
- `colorama` — цветной вывод в терминале (при необходимости)

## Лицензия

Учебный проект. Используйте на своё усмотрение.
