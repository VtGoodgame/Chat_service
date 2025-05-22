from dotenv import load_dotenv
import os

load_dotenv()

# BACKEND_URL = 'localhost:8000'
BACKEND_URL = 'http://back.b.aovzerk.ru'
# BACKEND_URL = 'https://gateway.brickbaza.ru'
PATH_PREFIX = '/api/chat-service'
AUTH_PREFIX = '/api/auth-service'
USER_PREFIX = '/api/user-service'
DB_SCHEMA = 'public'
COOKIE_NAME = "access_token"

# redis
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD')

#mongoDB
MONGO_URL = os.getenv('MONGO_URL')

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 YaBrowser/24.12.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "ru,en;q=0.9",
}

# jwt
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30
SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = "HS256"
