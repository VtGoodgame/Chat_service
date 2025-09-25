import httpx
from schemas.user import WhoAmI
from fastapi import Request, WebSocket
from src import concts as c


async def whoami(request: Request) -> WhoAmI:
    """Определяет текущего пользователя по HTTP cookies.

    Выполняет запрос к бекенду (`/auth/me`), используя куки запроса,
    и возвращает информацию о пользователе. Если запрос завершается
    с ошибкой (например, пользователь не авторизован), возвращается
    пустая модель `WhoAmI`.

    Args:
        request (Request): Объект FastAPI запроса, содержащий cookies.

    Returns:
        WhoAmI: Модель с данными пользователя (или пустая при ошибке).

    Raises:
        httpx.HTTPStatusError: Если бекенд возвращает ошибку авторизации.
        Exception: При других сетевых ошибках.
    """
    cookies = request.cookies

    async with httpx.AsyncClient(cookies=cookies) as client:
        try:
            response = await client.get(
                f"{c.BACKEND_URL}{c.AUTH_PREFIX}/auth/me",
                headers=c.HEADERS,
            )
            response.raise_for_status()
            return WhoAmI(**response.json())
        except httpx.HTTPStatusError as e:
            print("Ошибка авторизации /me:", e.response.status_code, e.response.text)
            return WhoAmI()
        except Exception as e:
            print("Ошибка запроса /me:", str(e))
            return WhoAmI()


async def whoami_socket(request: WebSocket) -> WhoAmI:
    """Определяет текущего пользователя по cookies WebSocket подключения.

    Выполняет запрос к бекенду (`/auth/me`), используя cookies,
    прикреплённые к WebSocket соединению, и возвращает информацию
    о пользователе. При ошибках возвращается пустая модель `WhoAmI`.

    Args:
        request (WebSocket): Объект WebSocket соединения, содержащий cookies.

    Returns:
        WhoAmI: Модель с данными пользователя (или пустая при ошибке).

    Raises:
        httpx.HTTPStatusError: Если бекенд возвращает ошибку авторизации.
        Exception: При других сетевых ошибках.
    """
    cookies = request.cookies

    async with httpx.AsyncClient(cookies=cookies) as client:
        try:
            response = await client.get(
                f"{c.BACKEND_URL}{c.AUTH_PREFIX}/auth/me",
                headers=c.HEADERS,
            )
            response.raise_for_status()
            return WhoAmI(**response.json())
        except httpx.HTTPStatusError as e:
            print("Ошибка авторизации /me:", e.response.status_code, e.response.text)
            return WhoAmI()
        except Exception as e:
            print("Ошибка запроса /me:", str(e))
            return WhoAmI()
