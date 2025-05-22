from contextlib import asynccontextmanager
import json
import logging
import requests
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.websockets import WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import src.auth as auth
import src.concts as c
import db.mongo as MongoDB
from schemas import message as MsgModel
from API import websocket_handler as WS
from db.mongo import get_mongo_db
from src.blacklist import check_user_blocked_by_username

@asynccontextmanager
async def lifespan(app: FastAPI):
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
    allow_origins=["http://dev.front.b.aovzerk.ru", "http://localhost:8080", "http://back.b.aovzerk.ru", "https://brickbaza.ru"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Хранилище подключений: { session_id: [websocket1, websocket2, ...] }
connections: Dict[str, List[WebSocket]] = {}

@app.get(c.PATH_PREFIX+"/wss/chats")
async def socket_get_chats_endpoint(user_id: int = 0, current_user = Depends(auth.whoami), client = Depends(get_mongo_db)):#, mongo_client = Depends(MongoDB.get_mongo_db)):
    """
    Получаем список чатов пользователя с полной структурой данных
    """
    if not current_user.user_id and user_id == 0:
        logging.error("Пользователь не аутентифицирован")
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        collection = client.chats_info
        
        # Ищем чаты, где пользователь является участником
        cursor = collection.find(
            {"members.user_id": user_id or current_user.user_id},
            {
                "chat_id": 1,
                "chat_type": 1,
                "chat_name": 1,
                "members": 1
            }
        )

        chat_list = []
        async for document in cursor:
            # Преобразуем данные в соответствии с моделью Chats
            chat = MsgModel.Chats(
                chat_id=document["chat_id"],
                chat_type=document.get("chat_type", "simple"),
                chat_name=document.get("chat_name"),
                members=[
                    MsgModel.Members(
                        user_id=member["user_id"],
                        user_name=member["user_name"],
                        avatar=member.get("avatar", "")
                    ) for member in document["members"]
                ]
            )
            chat_list.append(chat)
            logging.info("Выгрузка чатов")
       
        return chat_list  # Возвращаем список объектов Chats
       
    except Exception as e:
        logging.error(f"Ошибка при выгрузке чатов {e}")
        raise HTTPException(status_code=500, detail=str(e))

from uuid import uuid4

async def init_chat() -> MsgModel.Chats:
    """Инициализирует модель чата и возвращает ее"""
    chat = MsgModel.Chats(
        chat_id=str(uuid4()),  # Генерируем новый уникальный UUID
        chat_type='simple',
        chat_name=None,
        members=[]
    )
    return chat

@app.post(c.PATH_PREFIX + "/wss/create_chat")
async def create_chat_with_user(
    request: Request,
    username: str,
    user_id: int = 0,
    client=Depends(get_mongo_db),
    current_user = Depends(auth.whoami)
):
    if current_user.user_id is None and user_id == 0:
        logging.error("Пользователь не аутентифицирован")
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        response = requests.get(f"http://back.b.aovzerk.ru/api/user-service/user/?username={username}")
        if response.status_code != 200:
            raise HTTPException(status_code=404, detail="Пользователь не найден")

        user_data = response.json()
        target_user = {
            "user_id": user_data["id"],
            "user_name": user_data["username"],
            "avatar": user_data.get("avatar", "")
        }

        is_blocked = await check_user_blocked_by_username(
            request=request,
            blocked_username=target_user["user_name"]
        )
        if is_blocked['blocked_by_user'] or is_blocked['you_blocked_user']:
            raise HTTPException(status_code=403, detail=is_blocked)

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Ошибка при получении пользователя {username}: {e}")
        raise HTTPException(status_code=400, detail="Ошибка получения пользователя")

    mongo_chat_id = await MongoDB.get_chat_id(
        client,
        user_id or current_user.user_id,
        target_user["user_id"]
    )

    if not mongo_chat_id:
        new_chat = await init_chat()
        mongo_chat_id = new_chat.chat_id

        await MongoDB.add_members_to_chat(
            client,
            chat_id=mongo_chat_id,
            user_id=user_id or current_user.user_id,
            user_name=current_user.username,
            avatar=current_user.avatar
        )
        await MongoDB.add_members_to_chat(
            client,
            chat_id=mongo_chat_id,
            user_id=target_user["user_id"],
            user_name=target_user["user_name"],
            avatar=target_user["avatar"]
        )

    chat_info = await MongoDB.get_chat_info(client, mongo_chat_id)
    if not chat_info:
        raise HTTPException(status_code=404, detail="Чат не найден после создания")

    return chat_info


connected_clients : Dict[str, Dict[str, Any]] = {}


@app.websocket(c.PATH_PREFIX+"/wss/chat")
async def chat_room(
    websocket: WebSocket,
    chat_id: str,
    user_id: int = 0,
    current_user = Depends(auth.whoami_socket)
):
    if current_user.user_id is None and current_user == 0:
        logging.error("Пользователь не аутентифицирован")
        await websocket.close(code=1008, reason="Not authenticated")
        return
    
    mongo_client: MongoDB = websocket.app.state.mongo_client.baza
    chat_info: MsgModel.Chats = await MongoDB.get_chat_info(mongo_client, chat_id)
    if not chat_info:
        await websocket.close(code=1011, reason="Chat not found in DB")
        return
    recipient = next((m for m in chat_info.members if m.user_id != current_user.user_id), None)
    if not recipient:
        await websocket.close(code=1011, reason="User not found in current chat")
        return
    is_blocked = await check_user_blocked_by_username(
        request=websocket,
        blocked_username=recipient.user_name
    )
    if is_blocked['blocked_by_user'] or is_blocked['you_blocked_user']:
        await websocket.close(code=1011, reason="Blocked by user")
        return

    await websocket.accept()

    try:
        if chat_id not in connected_clients:
            connected_clients[chat_id] = {
                "websocket_list": []
            }

        connected_clients[chat_id]["websocket_list"].append(websocket)

        while True:
            data_str = await websocket.receive_text()
            data = json.loads(data_str)

            for client in connected_clients[chat_id]["websocket_list"]:
                try:
                    await client.send_text(json.dumps({
                        "chat_id": data.get('chat_id'),
                        "sender_id": data.get('sender_id'),
                        "content": data.get('content')
                    }))
                except Exception as e:
                    logging.error(f"Ошибка при отправке сообщения: {e}")

            # 💾 Сохраняем сообщение
            await MongoDB.add_message_mongo(
                mongo_client,
                chat_id=data.get('chat_id'),
                sender_id=data.get('sender_id'),
                content=data.get('content')
            )

    except WebSocketDisconnect:
        # logging.info(f"Пользователь {current_user.username} отключился")
        logging.info(f"Пользователь отключился")
    finally:
        if chat_id in connected_clients:
            connected_clients[chat_id]["websocket_list"] = [
                ws for ws in connected_clients[chat_id]["websocket_list"]
                if ws != websocket
            ]
            if not connected_clients[chat_id]["websocket_list"]:
                connected_clients.pop(chat_id)


@app.get(c.PATH_PREFIX+"/wss/chat_messages/{chat_id}")
async def get_message_limit( offset: int , limit: int, chat_id: str,user_id:int=0,current_user = Depends(auth.whoami), client=Depends(get_mongo_db)):
    if current_user.user_id is None and user_id==0:
        logging.error("Пользователь не аутентифицирован")
        raise HTTPException(status_code=401, detail="Not authenticated")
    messages = await MongoDB.get_messages(client, chat_id, limit, offset)
    return messages