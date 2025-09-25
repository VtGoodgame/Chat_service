
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
- **Язык / Фреймворк**: Python 3.11, FastAPI, AsyncIO  
- **Базы данных**: PostgreSQL, MongoDB  
- **ORM и валидация**: SQLAlchemy, Pydantic  
- **Инфраструктура**: Docker, Docker Compose  
- **Тестирование**: Pytest (юнит-, интеграционные и API-тесты)  
- **CI/CD**: GitHub Actions (линтеры, типизация, тесты, coverage)  

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
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=chat_service
JWT_SECRET=dev-secret-change-me

```
### 3. Запуск через Docker Compose

```bash
docker-compose up --build
```

После запуска:
- API доступно на: http://localhost:8000
- Swagger: http://localhost:8000/docs

### 🧪 Тестирование
```bash
pytest -v
```

### 📊 Архитектура (упрощённо)
```scss
[ FastAPI ] 
   │
   ├── REST API (Auth, Users)
   ├── WebSocket (Chat, Messages)
   │
   ├── PostgreSQL (Users, Chats)
   └── MongoDB (Message History)
```
