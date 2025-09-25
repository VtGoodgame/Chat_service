import logging
import requests
import src.concts as c
from fastapi import Request


async def check_user_blocked_by_username(request: Request, blocked_username: str) -> dict:
    """Проверяет, заблокирован ли пользователь по имени.

    Выполняет запрос к user-service (`/blacklist/check`) для проверки,
    находится ли указанный пользователь в чёрном списке. В качестве
    авторизации используются cookies из текущего запроса.

    Args:
        request (Request): Объект FastAPI запроса, содержащий cookies пользователя.
        blocked_username (str): Имя пользователя, для которого выполняется проверка.

    Returns:
        dict | bool: Словарь с результатом проверки (если статус 200),
        либо False в случае ошибки запроса или недоступности сервиса.

    Raises:
        Exception: В случае сетевой ошибки или таймаута при обращении к сервису.
    """
    try:
        response = requests.get(
            c.BACKEND_URL + c.USER_PREFIX + "/blacklist/check",
            params={"username": blocked_username},
            timeout=2,
            cookies=request.cookies
        )
        if response.status_code == 200:
            return response.json()
        else:
            logging.warning(f"Blacklist check failed: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"Ошибка запроса к user-service (check blacklist): {e}")
        return False
