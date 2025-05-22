import httpx
from schemas.user import WhoAmI
from fastapi import Request, WebSocket
from src import concts as c

async def whoami(request: Request) -> WhoAmI:
    cookies = request.cookies

    async with httpx.AsyncClient(cookies=cookies) as client:
        try:
            response = await client.get(
                f"{c.BACKEND_URL}{c.AUTH_PREFIX}/auth/me",
                headers=c.HEADERS
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
    cookies = request.cookies

    async with httpx.AsyncClient(cookies=cookies) as client:
        try:
            response = await client.get(
                f"{c.BACKEND_URL}{c.AUTH_PREFIX}/auth/me",
                headers=c.HEADERS
            )
            response.raise_for_status()
            return WhoAmI(**response.json())
        except httpx.HTTPStatusError as e:
            print("Ошибка авторизации /me:", e.response.status_code, e.response.text)
            return WhoAmI()
        except Exception as e:
            print("Ошибка запроса /me:", str(e))
            return WhoAmI()

