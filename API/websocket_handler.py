from fastapi import WebSocket, WebSocketDisconnect
import uuid
from datetime import datetime
import pytz
import asyncio
from typing import Dict, Tuple, Optional, List
from db import mongo
import logging
from schemas import message

class ConnectionManager:
    def __init__(self):
        # Список подключений
        self.unsendmsg: List[message.Messages]
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        try:
            # Принимаем новое соединение и добавляем его в список активных
            await websocket.accept()
            logging.info("Подключение открыто")
            self.active_connections.append(websocket)
        except Exception as e:
            logging.error(f"Ошибка открытии соединения : {e}")


    def disconnect(self, websocket: WebSocket):
        try:
           logging.info("Подключение закрыто")
        # Убираем отключенного клиента из списка
           self.active_connections.remove(websocket)
        except Exception as e:
            logging.error(f"Ошибка закрытия соединения : {e}")

    async def broadcast(self, message: str, chat_id: str, sender_id: int):
        try:
        # Отправляем сообщение всем подключенным пользователям
           for connection in self.active_connections:
               await connection.send_text(message)
               document = mongo.add_message_mongo(chat_id, sender_id, message)
               logging.info(f"Сообщение добавлено в бд с id: {document.id}")
        except Exception as e:
            logging.error(f"Ошибка отправке сообщения: {e}")
            
# Инициализация менеджера подключений
manager = ConnectionManager()