
![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

# 📦 Chat Service (FastAPI + WebSockets)

A microservice for real-time messaging.  
Built with **FastAPI**, featuring **WebSocket** for chats and **REST API** for user management.  
Uses **PostgreSQL** to store user and chat metadata, and **MongoDB** to store message history.

---

## 🚀 Features
- 🔑 User registration and authentication (**JWT**).  
- 👥 Chat creation and management.  
- 💬 Real-time messaging via **WebSocket**.  
- 🗄️ Message history stored in **MongoDB**, metadata in **PostgreSQL**.  
- 📑 Auto-generated API documentation via **Swagger UI** (`/docs`).  

---

## 🛠️ Tech Stack
- **Language / Framework**: Python 3.12, FastAPI, AsyncIO  
- **Databases**: PostgreSQL, MongoDB  
- **ORM & Validation**: SQLAlchemy, Pydantic  
- **Infrastructure**: Docker, Docker Compose  
- **CI/CD**: GitLab CI/CD (linters, tests, Docker image publishing), Portainer for container monitoring  
- **Testing**:  
  - Pytest (unit, integration, API tests)  
  - Locust (load testing scenarios)  
  - Manual testing in staging via GitLab CI/CD pipeline in collaboration with DevOps  

---

## ⚙️ Installation & Run

### 1. Clone the project
```bash
git clone https://github.com/VtGoodgame/Chat_service.git
cd Chat_service
```

### 2. Configure environment variables
**Example .env:**
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
ACCESS_TOKEN_EXPIRE_MINUTES=43200  # 30 days
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

### 3. Run with Docker Compose
```bash
docker-compose up --build
```

After startup:
- API available at: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

### 🧪 Testing
**Run unit and integration tests:**
```bash
pytest -v
```
**Run load testing (Locust example):**
```bash
locust -f load_tests/locustfile.py --host=http://localhost:8000
```
*After startup, the Locust web UI is available at: http://localhost:8089*

### 📊 Project Structure (simplified)
```scss
Chat_service/
  ├─ .gitlab-ci/                              // GitLab CI templates/pipelines
  ├─ db/                                      // database connections & utils
  │   ├─ mongo.py
  │   └─ posgres.py                           // PostgreSQL connector
  ├─ schemas/                                 // Pydantic schemas (I/O validation)
  │   ├─ message.py
  │   └─ user.py
  ├─ src/                                     // routes / business logic
  │   ├─ auth.py
  │   ├─ blacklist.py
  │   └─ concts.py                            // constants & handlers
  ├─ test/                                    // test suite
  │   ├─ integration_main_test.py             // integration tests
  │   ├─ locust_test.py                       // load tests (Locust)
  │   └─ unit_mongo_test.py                   // unit tests
  ├─ Dockerfile                               // Docker image build
  ├─ .gitignore
  ├─ .gitlab-ci.yml                           // main CI pipeline config
  ├─ docker-compose.yml                       // local service orchestration
  ├─ main.py                                  // FastAPI entrypoint
  ├─ README.md
  └─ requirements.txt                         // project dependencies
```

### 📘 Дополнительно (на русском)

Этот проект был реализован в рамках практики и используется сайтом **https://brickbaza.ru**.  
Описание на русском доступно в [README_RU.md](README_RU.md).