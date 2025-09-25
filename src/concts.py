"""Конфигурационный модуль для сервиса чата.

Загружает переменные окружения из `.env` и определяет основные константы,
используемые в приложении: адреса сервисов, настройки Redis, MongoDB, JWT и др.
"""

import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env
load_dotenv()

#Backend endpoints
#BACKEND_URL = "http://localhost:8000"
BACKEND_URL = "http://back.b.aovzerk.ru"

#Префиксы для различных микросервисов
PATH_PREFIX = "/api/chat-service"
AUTH_PREFIX = "/api/auth-service"
USER_PREFIX = "/api/user-service"


#Database
DB_SCHEMA = "public"
COOKIE_NAME = "access_token"

#Redis
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

#MongoDB
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")


#HTTP
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/130.0.0.0 YaBrowser/24.12.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8,"
        "application/signed-exchange;v=b3;q=0.7"
    ),
    "Accept-Language": "ru,en;q=0.9",
}

#JWT
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 дней
SECRET_KEY: str | None = os.getenv("SECRET_KEY")
ALGORITHM: str = "HS256"