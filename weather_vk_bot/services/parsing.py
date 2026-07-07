"""Разбор пользовательского текстового ввода (координаты, списки городов)."""

from __future__ import annotations


def parse_coordinates(text: str) -> tuple[float, float] | None:
    """Разбирает координаты из строки. Разделитель — запятая или пробел.

    Возвращает (lat, lon) при корректных значениях в допустимых диапазонах,
    иначе None.
    """
    if not text:
        return None
    parts = [p for p in text.replace(",", " ").split() if p]
    if len(parts) != 2:
        return None
    try:
        lat, lon = float(parts[0]), float(parts[1])
    except ValueError:
        return None
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return None
    return lat, lon


def parse_two_cities(text: str) -> tuple[str, str] | None:
    """Разбирает два города из строки (разделитель — запятая или перевод строки).

    Возвращает (город_a, город_b) или None, если городов не ровно два.
    """
    if not text:
        return None
    raw = text.replace("\n", ",")
    cities = [c.strip() for c in raw.split(",") if c.strip()]
    if len(cities) != 2:
        return None
    return cities[0], cities[1]
