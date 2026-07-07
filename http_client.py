import time

import requests

RETRY_DELAYS = (1, 2, 4)
MAX_RETRIES = len(RETRY_DELAYS)


def handle_response(response: requests.Response) -> tuple[bool, str]:
    if response.ok:
        return True, "Успешно"

    basic_errors = {
        400: "Некорректный запрос.",
        401: "Требуется авторизация. Необходимо указать API ключ в переменной окружения API_KEY",
        403: "Доступ запрещен.",
        404: "Ресурс не найден.",
        429: "Слишком много запросов.",
        500: "Внутренняя ошибка сервера.",
        502: "Плохой шлюз.",
        503: "Сервис временно недоступен.",
        504: "Таймаут шлюза.",
    }

    reason = basic_errors.get(response.status_code, "Неизвестная ошибка.")
    return False, f"Ошибка {response.status_code}: {reason}"


def _should_retry_response(response: requests.Response) -> bool:
    return response.status_code == 429


def _should_retry_exception(error: requests.RequestException) -> bool:
    return isinstance(
        error,
        (requests.ConnectionError, requests.Timeout, requests.ChunkedEncodingError),
    )


def _request_with_retries(
    make_request,
    method_label: str,
) -> requests.Response | None:
    retry_reason = ""

    for attempt in range(MAX_RETRIES + 1):
        if attempt > 0:
            delay = RETRY_DELAYS[attempt - 1]
            print(f"{retry_reason} Повтор через {delay} с...")
            time.sleep(delay)

        try:
            response = make_request()
        except requests.RequestException as error:
            if _should_retry_exception(error) and attempt < MAX_RETRIES:
                retry_reason = f"Сетевая ошибка ({method_label}): {error}."
                continue
            print(f"Ошибка {method_label} запроса: {error}")
            return None

        if _should_retry_response(response):
            if attempt < MAX_RETRIES:
                retry_reason = "Ошибка 429: слишком много запросов."
                continue
            _, message = handle_response(response)
            print(message)
            return None

        is_success, message = handle_response(response)
        if not is_success:
            print(message)
            return None
        return response

    return None


def get_request(url: str, params=None, timeout=10) -> requests.Response | None:
    if not url:
        print("URL не должен быть пустым.")
        return None

    return _request_with_retries(
        lambda: requests.get(url, params=params, timeout=timeout),
        "GET",
    )


def post_request(
    url: str,
    body: dict | None = None,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: int = 15,
) -> requests.Response | None:
    if not url:
        print("URL не должен быть пустым.")
        return None

    return _request_with_retries(
        lambda: requests.post(
            url,
            json=body if body is not None else {},
            params=params,
            headers=headers,
            timeout=timeout,
        ),
        "POST",
    )