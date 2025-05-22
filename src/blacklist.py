import logging
import requests
import src.concts as c
from fastapi import Request

async def check_user_blocked_by_username(request: Request, blocked_username: str) -> dict:
    """
    Проверяет, заблокирован ли sender_id у пользователя с именем blocked_username.
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
