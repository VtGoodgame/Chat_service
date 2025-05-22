import logging
from uuid import UUID
from uuid import uuid4
from typing import Optional
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from schemas import message as MsgModel
import src.concts as c
from fastapi import Request

async def get_mongo_db(request: Request):
    return request.app.state.mongo_client.baza

async def get_mongo_chats(client:AsyncIOMotorClient, user_id: int, chat_id: UUID) -> Optional[MsgModel.Chats]:
    try:
        logging.info("Подключение к Mongo")
        collection=client.chat_info

        query={"user_id": user_id, "chat_id": str(chat_id)}
        document = await collection.find_one(query)

        if not document:
            return None

        logging.info(f"Return {document}")
        chat = MsgModel.ChatItem.from_dict(document)
        return chat

    except Exception as e:
        logging.error(f"Ошибка при получении чатов: {e}")
        return None


async def add_message_mongo(
    client:AsyncIOMotorClient,
    chat_id: str,
    sender_id: int,
    content: str
) -> Optional[MsgModel.Messages]:
    """
    Добавляет сообщение в чат и возвращает его как объект Messages.
    """
    try:
        logging.info("Подключение к MongoDB")
        collection=client.chats_msgs
        msg_id = str(uuid4())

        new_message={
            "msg_id": msg_id,
            "chat_id": str(chat_id),
            "content": content,
            "sender_id": sender_id,
            "timestamp": datetime.now(timezone.utc)+timedelta(hours=3),
            "readers": []
        }

        result=await collection.insert_one(new_message)

        chat_data=await collection.find_one({"msg_id": msg_id})
        if not chat_data:
            logging.error(f"Чат {MsgModel.Messages(**chat_data)} не найден после обновления")
            return None
        logging.info(f"Сообщение добавлено: {chat_data}")
        return chat_data

    except Exception as e:
        logging.error(f"Ошибка при записи сообщения: {e}")
        return None


async def add_members_to_chat(
    client:AsyncIOMotorClient,
    chat_id: UUID,
    user_id: int,
    user_name: str,
    avatar: str
) -> MsgModel.Chats:
    try:
        
        logging.info("Подключение к MongoDB")
        collection=client.chats_info

        # Создаем объект участника 
        new_member={
            "user_id": user_id,
            "user_name": user_name,
            "avatar": avatar
        }

        # Обновляем чат (или создаём новый, если не существует)
        result=await collection.update_one(
            {"chat_id": chat_id},
            {
                "$addToSet": {"members": new_member},  # Добавляем участника, если его нет
                "$setOnInsert": {  # Эти поля устанавливаются только при создании нового чата
                    "chat_type": "simple",
                    "chat_name": None,
                    "messages": []
                }
            },
            upsert=True
        )
        print(f"Добавление пользователя {result}")
        # Получаем обновлённый чат из БД
        chat_data = await collection.find_one({"chat_id": chat_id})
        
        if not chat_data:
            raise ValueError(f"Чат {chat_id} не найден после обновления")

        # Преобразуем данные из MongoDB в модель `Chats`
        chat=MsgModel.Chats(
            chat_id=chat_data["chat_id"],
            chat_type=chat_data.get("chat_type", "simple"),
            chat_name=chat_data.get("chat_name"),
            members=[
                MsgModel.Members(
                    user_id=member["user_id"],
                    user_name=member["user_name"],
                    avatar=member["avatar"]
                )
                for member in chat_data["members"]
            ]
        )

        logging.info(f"Участник {user_id} добавлен в чат {chat_id}")
        return chat

    except Exception as e:
        logging.error(f"Ошибка при добавлении участника {user_id} в чат {chat_id}: {str(e)} {str(e.__context__)}")
        raise


async def get_chat_info(client:AsyncIOMotorClient,chat_id: UUID) -> Optional[MsgModel.Chats]:
    """
    Получает полную информацию о чате
    
    Параметры:
        chat_id: UUID - идентификатор чата
        
    Возвращает:
        Chats | None - объект чата или None, если чат не найден
    """
    try:
        logging.info(f"Подключение к MongoDB для получения чата {chat_id}")
        collection=client.chats_info

        #Ищем чат по chat_id
        chat_data=await collection.find_one({"chat_id": str(chat_id)})  # Преобразуем UUID в строку
        
        if not chat_data:
            logging.warning(f"Чат {chat_id} не найден в базе данных")
            return None

        #Создаем список участников 
        members=[]
        for member_data in chat_data.get("members", []): 
            member=MsgModel.Members(
                user_id=member_data["user_id"],
                user_name=member_data["user_name"],
                avatar=member_data["avatar"]
            )
            members.append(member)

        #Создаем объект чата
        chat=MsgModel.Chats(
            chat_id=chat_data["chat_id"],
            chat_type=chat_data.get("chat_type", "simple"),
            chat_name=chat_data.get("chat_name"),
            members=members
        )

        logging.info(f"Успешно получен чат {chat_id} с {len(members)} участниками")
        return chat
    
    except Exception as e:
        logging.error(f"Ошибка при получении информации по чату: {e}")
        


async def get_chat_id(client:AsyncIOMotorClient,current_id: int, user_id: int, chat_type: str = "simple"):
    try:
        logging.info("Подключение к MongoDB для получения чата")
        collection=client.chats_info

        # Ищем чат, где есть оба участника
        chat_data=await collection.find_one(
            {
                "members.user_id": {"$all": [user_id, current_id]},
                "chat_type": chat_type  # Используем параметр вместо жесткого значения
            }
        )
        
        if chat_data:
            logging.info(f"Найден чат: {chat_data}")
            return chat_data['chat_id']
        return None

    except Exception as e:
        logging.error(f"Ошибка при поиске чата: {e}")
        raise


async def get_messages(client:AsyncIOMotorClient,chat_id: str, limit: int, offset: int):
    try:
        collection=client.chats_msgs

        cursor=collection.find({"chat_id": chat_id}).sort("timestamp", -1).skip(offset).limit(limit)
        print(cursor)
        message_list=[]
        
        async for message_data in cursor:
            try:
                print(message_data)
                # Обработка readers (с проверкой полей)
                readers=[]
                for reader in message_data.get("readers", []):
                    # Проверяем обязательные поля для reader
                    if not all(field in reader for field in ["user_id", "user_name"]):
                        logging.warning("Пропущен reader с отсутствующими полями")
                        continue
                    
                    readers.append({
                        "user_id": reader["user_id"],
                        "user_name": reader["user_name"],
                        "avatar": reader.get("avatar")  # Необязательное поле
                    })

                # Создаем объект сообщения
                message={
                    "msg_id": str(message_data["msg_id"]),
                    "chat_id": str(message_data["chat_id"]),
                    "content": message_data.get("content"),
                    "sender_id": int(message_data["sender_id"]),
                    "timestamp": message_data["timestamp"].isoformat() if hasattr(message_data["timestamp"], "isoformat") else str(message_data["timestamp"]),
                    "readers": readers
                }
                print(MsgModel.Messages(**message))
                message_list.append(message)
                
            except Exception as doc_error:
                logging.error(f"Ошибка обработки документа: {str(doc_error)}")
                continue

        return message_list
 
    except Exception as e:
        logging.error(f"Ошибка при получении сообщений: {str(e)}", exc_info=True)
        raise
