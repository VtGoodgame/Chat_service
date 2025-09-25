import json
import asyncio
import logging
from typing import Any, Dict
from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocket, WebSocketDisconnect
from motor.motor_asyncio import AsyncIOMotorClient

import db.mongo as MongoDB
from db.mongo import get_mongo_db
from schemas import message as MsgModel
import src.auth as auth
import src.concts as c
from src.blacklist import check_user_blocked_by_username

from uuid import uuid4

#region helpers
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Лайф-цикл приложения: подключение/закрытие MongoDB клиента.

    При старте приложения создаёт клиент `AsyncIOMotorClient` и кладёт его в
    `app.state.mongo_client`. При завершении — корректно закрывает соединение.

    Args:
        app (FastAPI): Экземпляр приложения FastAPI.

    Yields:
        None: Управление возвращается FastAPI для запуска приложения.
    """
    try:
        # Инициализация при старте
        app.state.mongo_client = AsyncIOMotorClient(c.MONGO_URL)
        logging.info(f"MongoDB подключен: {app.state.mongo_client}")
        yield
    finally:
        # Закрытие при завершении
        if app.state.mongo_client:
            app.state.mongo_client.close()
            logging.info("MongoDB соединение закрыто")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://dev.front.b.aovzerk.ru",
        "http://localhost:8080",
        "http://back.b.aovzerk.ru",
        "https://brickbaza.ru",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

connected_clients: Dict[str, Dict[str, Any]] = {}

async def init_chat() -> MsgModel.Chats:
    """Инициализирует пустую модель чата.

    Генерирует новый `chat_id` (UUID4), задаёт тип `simple` и пустой список участников.

    Returns:
        MsgModel.Chats: Объект чата с новыми идентификатором и базовыми полями.
    """
    chat = MsgModel.Chats(
        chat_id=str(uuid4()),
        chat_type="simple",
        chat_name=None,
        members=[],
    )
    return chat

#endregion

#region endpoints
@app.get(c.PATH_PREFIX + "/wss/chats")
async def socket_get_chats_endpoint(
    user_id: int = 0,
    current_user=Depends(auth.whoami),
    client=Depends(get_mongo_db),
):
    """Возвращает список чатов пользователя с полной структурой данных.

    Если `user_id` не передан (== 0), используется `current_user.user_id`,
    определённый через зависимость `auth.whoami`.

    Args:
        user_id (int, optional): ID пользователя, для которого запрашиваются чаты.
        current_user: Текущий авторизованный пользователь (через Depends).
        client: Экземпляр базы MongoDB (через Depends).

    Returns:
        list[MsgModel.Chats]: Список чатов пользователя.

    Raises:
        HTTPException: 401 — если пользователь не аутентифицирован.
        HTTPException: 500 — при ошибках чтения из MongoDB.
    """
    effective_user_id = user_id or getattr(current_user, "user_id", 0)
    if not effective_user_id:
        logging.error("Пользователь не аутентифицирован")
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        collection = client.chats_info
        filter_ = {"members.user_id": effective_user_id}
        projection = {"chat_id": 1, "chat_type": 1, "chat_name": 1, "members": 1}

        #Один сетевой запрос получаем все документы списком
        docs = await collection.find(filter_, projection).to_list(length=None)

        chat_list = [
            MsgModel.Chats(
                chat_id=doc["chat_id"],
                chat_type=doc.get("chat_type", "simple"),
                chat_name=doc.get("chat_name"),
                members=[
                    MsgModel.Members(
                        user_id=m["user_id"],
                        user_name=m["user_name"],
                        avatar=m.get("avatar", ""),
                    )
                    for m in doc.get("members", [])
                ],
            )
            for doc in docs
        ]

        logging.info("Выгрузка чатов: %d шт.", len(chat_list))
        return chat_list

    except Exception as e:
        logging.error("Ошибка при выгрузке чатов: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



@app.post(c.PATH_PREFIX + "/wss/create_chat")
async def create_chat_with_user(
    request: Request,
    username: str,
    user_id: int = 0,
    client=Depends(get_mongo_db),
    current_user=Depends(auth.whoami),
):
    """Создаёт новый чат или возвращает существующий чат с указанным пользователем.

    Шаги:
      1) Получает карточку целевого пользователя по `username` из user-service.
      2) Проверяет взаимные блокировки (`check_user_blocked_by_username`).
      3) Ищет существующий чат между инициатором и целевым пользователем.
      4) Если чата нет — создаёт новый и добавляет обоих участников.
      5) Возвращает полную информацию о чате.

    Args:
        request: HTTP-запрос (для cookies при проверке блокировки).
        username: Имя пользователя, с которым нужно создать чат.
        user_id: Явно заданный ID инициатора (если 0 — берётся из `current_user`).
        client: Экземпляр базы MongoDB (через Depends).
        current_user: Текущий авторизованный пользователь (через Depends).

    Returns:
        MsgModel.Chats: Информация о созданном/найденном чате.

    Raises:
        HTTPException: 401 — пользователь не аутентифицирован.
        HTTPException: 404 — целевой пользователь не найден или чат не найден после создания.
        HTTPException: 403 — пользователи заблокированы.
        HTTPException: 400 — ошибка на этапе получения пользователя.
        HTTPException: 500 — внутренняя ошибка при работе с БД/сервисами.
    """
    effective_user_id = user_id or getattr(current_user, "user_id", 0)
    if not effective_user_id:
        logging.error("Пользователь не аутентифицирован")
        raise HTTPException(status_code=401, detail="Not authenticated")

    #Получаем целевого пользователя
    try:
        async with httpx.AsyncClient(timeout=5.0) as hc:
            resp = await hc.get(f"{c.BACKEND_URL}{c.USER_PREFIX}/user/", params={"username": username})
            if resp.status_code != 200:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            user_data = resp.json()
            target_user = {
                "user_id": user_data["id"],
                "user_name": user_data["username"],
                "avatar": user_data.get("avatar", ""),
            }
    except HTTPException:
        raise
    except Exception as e:
        logging.error("Ошибка при получении пользователя %s: %s", username, e, exc_info=True)
        raise HTTPException(status_code=400, detail="Ошибка получения пользователя")

    #Проверяем взаимные блокировки
    try:
        is_blocked = await check_user_blocked_by_username(
            request=request, blocked_username=target_user["user_name"]
        )
        if isinstance(is_blocked, dict) and (
            is_blocked.get("blocked_by_user") or is_blocked.get("you_blocked_user")
        ):
            raise HTTPException(status_code=403, detail=is_blocked)
    except HTTPException:
        raise
    except Exception as e:
        logging.error("Ошибка проверки блокировок для %s: %s", username, e, exc_info=True)
        raise HTTPException(status_code=500, detail="Ошибка проверки блокировок")

    #Ищем существующий чат
    try:
        mongo_chat_id = await MongoDB.get_chat_id(client, effective_user_id, target_user["user_id"])
    except Exception as e:
        logging.error("Ошибка поиска чата в MongoDB: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Ошибка поиска чата")

    #Если чата нет — создаём и добавляем обоих участников
    if not mongo_chat_id:
        try:
            new_chat = await init_chat()
            mongo_chat_id = new_chat.chat_id

            await asyncio.gather(
                MongoDB.add_members_to_chat(
                    client,
                    chat_id=mongo_chat_id,
                    user_id=effective_user_id,
                    user_name=current_user.username,
                    avatar=current_user.avatar,
                ),
                MongoDB.add_members_to_chat(
                    client,
                    chat_id=mongo_chat_id,
                    user_id=target_user["user_id"],
                    user_name=target_user["user_name"],
                    avatar=target_user["avatar"],
                ),
            )
        except Exception as e:
            logging.error("Ошибка создания/инициализации чата: %s", e, exc_info=True)
            raise HTTPException(status_code=500, detail="Ошибка создания чата")

    #Возвращаем полную информацию о чате
    chat_info = await MongoDB.get_chat_info(client, mongo_chat_id)
    if not chat_info:
        raise HTTPException(status_code=404, detail="Чат не найден после создания")

    logging.info("Чат %s готов для пользователей %s и %s", mongo_chat_id, effective_user_id, target_user["user_id"])
    return chat_info


@app.websocket(c.PATH_PREFIX + "/wss/chat")
async def chat_room(
    websocket: WebSocket,
    chat_id: str,
    current_user=Depends(auth.whoami_socket),
):
    """Вебсокет-комната чата.

    Проверяет авторизацию, существование чата и блокировки, затем:
    - подключает клиента к комнате;
    - ретранслирует входящие сообщения всем участникам комнаты;
    - сохраняет каждое сообщение в MongoDB.
    """
    #Проверка аутентификации пользователя
    if current_user.user_id is None and current_user == 0:
        logging.error("Пользователь не аутентифицирован")
        await websocket.close(code=1008, reason="Not authenticated")
        return

    #Получаем информацию о чате и проверяем блокировки
    mongo_db = websocket.app.state.mongo_client.baza
    chat_info: MsgModel.Chats = await MongoDB.get_chat_info(mongo_db, chat_id)
    if not chat_info:
        await websocket.close(code=1011, reason="Chat not found in DB")
        return

    recipient = next((m for m in chat_info.members if m.user_id != current_user.user_id), None)
    if not recipient:
        await websocket.close(code=1011, reason="User not found in current chat")
        return

    is_blocked = await check_user_blocked_by_username(
        request=websocket, blocked_username=recipient.user_name
    )
    if is_blocked.get("blocked_by_user") or is_blocked.get("you_blocked_user"):
        await websocket.close(code=1011, reason="Blocked by user")
        return

    await websocket.accept()

    try:
        #Регистрируем соединение в комнате
        room = connected_clients.setdefault(chat_id, {"websocket_list": []})
        room_sockets = room["websocket_list"]
        room_sockets.append(websocket)

        while True:
            #Получаем и разбираем входящее сообщение
            data = json.loads(await websocket.receive_text())

            #Готовим полезную нагрузку для рассылки
            outgoing = json.dumps(
                {
                    "chat_id": data.get("chat_id"),
                    "sender_id": data.get("sender_id"),
                    "content": data.get("content"),
                }
            )

            #Рассылаем всем участникам комнаты
            for ws in list(room_sockets):
                try:
                    await ws.send_text(outgoing)
                except Exception as e:
                    logging.error("Ошибка при отправке сообщения: %s", e)

            #Сохраняем сообщение
            await MongoDB.add_message_mongo(
                mongo_db,
                chat_id=data.get("chat_id"),
                sender_id=data.get("sender_id"),
                content=data.get("content"),
            )

    except WebSocketDisconnect:
        logging.info("Пользователь отключился")
    finally:
        #Акуратно вычищаем комнату от текущего сокета
        if chat_id in connected_clients:
            room_sockets = connected_clients[chat_id]["websocket_list"]
            connected_clients[chat_id]["websocket_list"] = [ws for ws in room_sockets if ws is not websocket]
            if not connected_clients[chat_id]["websocket_list"]:
                connected_clients.pop(chat_id)



@app.get(c.PATH_PREFIX + "/wss/chat_messages/{chat_id}")
async def get_message_limit(
    offset: int,
    limit: int,
    chat_id: str,
    current_user=Depends(auth.whoami),
    client=Depends(get_mongo_db),
):
    """Возвращает сообщения чата с пагинацией.

    Args:
        offset (int): Смещение для пагинации (кол-во записей, которые нужно пропустить).
        limit (int): Максимальное количество сообщений в ответе.
        chat_id (str): Идентификатор чата.
        current_user: Текущий авторизованный пользователь (через Depends).
        client: Экземпляр базы MongoDB (через Depends).

    Returns:
        list[dict]: Список сообщений (как словари), упорядоченных по убыванию `timestamp`.

    Raises:
        HTTPException: 401 — если пользователь не аутентифицирован.
    """
    if current_user.user_id is None:
        logging.error("Пользователь не аутентифицирован")
        raise HTTPException(status_code=401, detail="Not authenticated")
    messages = await MongoDB.get_messages(client, chat_id, limit, offset)
    return messages

#endregion