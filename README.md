![CI](https://img.shields.io/github/actions/workflow/status/VtGoodgame/Chat_service/ci.yml?branch=main)
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

# 📦 Chat Service (FastAPI + WebSockets)

Микросервис для обмена сообщениями в реальном времени.  
Реализован на **FastAPI** с поддержкой **WebSocket** для чатов и **REST API** для управления пользователями.  
Используются **PostgreSQL** для хранения данных и **MongoDB** для истории сообщений.

---

## 🚀 Функционал
- Регистрация и аутентификация пользователей (**JWT**).  
- Создание и управление чатами.  
- Отправка и получение сообщений в реальном времени через **WebSocket**.  
- Хранение сообщений в **MongoDB**, метаданных — в **PostgreSQL**.  
- Документация API доступна через **Swagger UI** (`/docs`).  

---

## 🛠️ Технологии
- Python 3.11, FastAPI, AsyncIO  
- PostgreSQL, MongoDB  
- SQLAlchemy, Pydantic  
- Docker, Docker Compose  
- Pytest (юнит + интеграционные тесты)  

---

## ⚙️ Установка и запуск

### 1. Клонировать проект
```bash
git clone https://github.com/VtGoodgame/Chat_service.git
cd Chat_service
```
### 2. Настроить переменные окружения
```text
Скопировать .env.example в .env и указать свои значения (БД, JWT-secret и т.д.)
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
