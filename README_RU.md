![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

# 📦 Chat Service (FastAPI + WebSockets)

Микросервис для обмена сообщениями в реальном времени.  
Реализован на **FastAPI** с поддержкой **WebSocket** для чатов и **REST API** для управления пользователями.  
Используются **PostgreSQL** для хранения данных о пользователях и чатах, а **MongoDB** — для истории сообщений.

---

## 🚀 Функционал
- 🔑 Регистрация и аутентификация пользователей (**JWT**).  
- 👥 Создание и управление чатами.  
- 💬 Отправка и получение сообщений в реальном времени через **WebSocket**.  
- 🗄️ Хранение сообщений в **MongoDB**, метаданных — в **PostgreSQL**.  
- 📑 Автоматическая документация API через **Swagger UI** (`/docs`).  

---

## 🛠️ Стек технологий
- **Язык / Фреймворк**: Python 3.12, FastAPI, AsyncIO  
- **Базы данных**: PostgreSQL, MongoDB  
- **ORM и валидация**: SQLAlchemy, Pydantic  
- **Инфраструктура**: Docker, Docker Compose  
- **CI/CD**: GitLab CI/CD (линтеры, тесты, публикация Docker-образов), Portainer для мониторинга контейнеров  
- **Тестирование**:  
  - Pytest (юнит, интеграционные и API-тесты)  
  - Locust (нагрузочные сценарии)  
  - Ручное тестирование на тестовом окружении через CI/CD пайплайн при поддержке DevOps  

---

## ⚙️ Установка и запуск

### 1. Клонировать проект
```bash
git clone https://github.com/VtGoodgame/Chat_service.git
cd Chat_service
```
### 2. Настроить переменные окружения
Пример .env 
```env
# ======================
# 📦 DATABASE SETTINGS
# ======================
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=chat_service
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# ======================
# 🔐 JWT / AUTH
# ======================
SECRET_KEY=change-me-in-prod
ACCESS_TOKEN_EXPIRE_MINUTES=43200  # 30 дней
ALGORITHM=HS256

# ======================
# 🔄 REDIS
# ======================
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# ======================
# 🍃 MONGODB
# ======================
MONGO_URL=mongodb://localhost:27017

# ======================
# 🌐 BACKEND URL
# ======================
BACKEND_URL=http://localhost:8000

# ======================
# ⚙️ SERVICE PREFIXES
# ======================
PATH_PREFIX=/api/chat-service
AUTH_PREFIX=/api/auth-service
USER_PREFIX=/api/user-service
```
### 3. Запуск через Docker Compose

```bash
docker-compose up --build
```

После запуска:
- API доступно на: http://localhost:8000
- Swagger: http://localhost:8000/docs

### 🧪 Тестирование
**Запуск юнит- и интеграционных тестов:**
```bash
pytest -v
```

**Запуск нагрузочного тестирования (пример для Locust):**
```bash
locust -f load_tests/locustfile.py --host=http://localhost:8000
```
После запуска интерфейс Locust доступен на: http://localhost:8089

### 📊 Архитектура (упрощённо)
```scss
Chat_service/
  ├─ .gitlab-ci/                              // пайплайны/шаблоны для GitLab CI
  ├─ db/                                      // подключения и утилиты для БД
  │   ├─ mongo.py
  │   └─ posgres.py                           // подключение к PostgreSQL
  ├─ schemas/                                 // Pydantic-схемы (валидация I/O)
  │   ├─ message.py
  │   └─ user.py
  ├─ src/                                     // роуты/бизнес-логика
  │   ├─ auth.py
  │   ├─ blacklist.py
  │   └─ concts.py                            // константы
  ├─ test/                                    // тесты
  │   ├─ integration_main_test.py             // интеграционные
  │   ├─ locust_test.py                       // нагрузочные (Locust)
  │   └─ unit_mongo_test.py                   // юнит-тесты
  ├─ Dockerfile                               // сборка образа приложения
  ├─ .gitignore
  ├─ .gitlab-ci.yml                           // основной файл CI
  ├─ docker-compose.yml                       // локальная оркестрация сервисов
  ├─ main.py                                  // точка входа FastAPI-приложения
  ├─ README.md
  └─ requirements.txt                         // зависимости проекта

```
