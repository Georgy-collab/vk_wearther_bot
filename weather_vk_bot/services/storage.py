"""Простое персистентное хранилище «избранного города» пользователя.

Данные хранятся в JSON-файле (ключ — id пользователя VK). Этого достаточно для
учебного бота; при масштабировании слой легко заменить на БД, сохранив интерфейс.
"""

from __future__ import annotations

import json
import logging
import threading
from pathlib import Path

logger = logging.getLogger(__name__)


class CityStorage:
    """Хранит выбранный пользователем город (user_id -> city)."""

    def __init__(self, path: str | Path) -> None:
        self._path = Path(path)
        self._lock = threading.Lock()
        self._data: dict[str, str] = self._load()

    def _load(self) -> dict[str, str]:
        if not self._path.exists():
            return {}
        try:
            return json.loads(self._path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            logger.warning("Не удалось прочитать %s: %s", self._path, error)
            return {}

    def _flush(self) -> None:
        try:
            self._path.write_text(
                json.dumps(self._data, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except OSError as error:
            logger.error("Не удалось сохранить %s: %s", self._path, error)

    def get_city(self, user_id: int) -> str | None:
        return self._data.get(str(user_id))

    def set_city(self, user_id: int, city: str) -> None:
        with self._lock:
            self._data[str(user_id)] = city
            self._flush()
