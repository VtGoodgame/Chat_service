import logging
from uuid import UUID
from uuid import uuid4
from typing import Optional
from datetime import datetime, timedelta, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from schemas import message as MsgModel
import src.concts as c
from fastapi import Request

#region Helpers
logger = logging.getLogger(__name__)

async def get_mongo_db(request: Request):
    return request.app.state.mongo_client.baza

async def _iso(dt) -> str:
    """Безопасное преобразование timestamp к ISO-строке."""
    if hasattr(dt, "isoformat"):
        return dt.isoformat()
    return str(dt)


async def _valid_reader(reader: Dict[str, Any]) -> bool:
    """Проверка минимально необходимых полей reader."""
    return isinstance(reader, dict) and "user_id" in reader and "user_name" in reader
#endregion

#region public API
async def get_mongo_chats(
    client: AsyncIOMotorClient,
    user_id: int,
    chat_id: UUID
) -> Optional[MsgModel.Chats]:
    """Получает информацию о чате для указанного пользователя.

    Args:
        client (AsyncIOMotorClient): Клиент MongoDB.
        user_id (int): Идентификатор пользователя.
        chat_id (UUID): Уникальный идентификатор чата.

    Returns:
        Optional[MsgModel.Chats]: Объект чата, если найден, иначе None.

    Raises:
        Exception: В случае ошибки подключения или запроса к базе данных.
    """
    try:
        logger.info("Подключение к Mongo")
        collection = client.chat_info

        query = {"user_id": user_id, "chat_id": str(chat_id)}
        document = await collection.find_one(query)
        if not document:
            return None

        logger.info("Чат найден")
        chat = MsgModel.ChatItem.from_dict(document)
        return chat
    except Exception as e:
        logger.error("Ошибка при получении чатов: %s", e, exc_info=True)
        return None


async def add_message_mongo(
    client: AsyncIOMotorClient,
    chat_id: str,
    sender_id: int,
    content: str
) -> Optional[MsgModel.Messages]:
    """Добавляет новое сообщение в чат.

    Args:
        client (AsyncIOMotorClient): Клиент MongoDB.
        chat_id (str): Идентификатор чата.
        sender_id (int): Идентификатор отправителя.
        content (str): Текст сообщения.

    Returns:
        Optional[MsgModel.Messages]: Документ сообщения из БД, либо None если не найден.

    Raises:
        Exception: В случае ошибки при вставке или чтении из базы данных.
    """
    try:
        logger.info("Подключение к MongoDB")
        collection = client.chats_msgs
        msg_id = str(uuid4())

        new_message = {
            "msg_id": msg_id,
            "chat_id": str(chat_id),
            "content": content,
            "sender_id": sender_id,
            "timestamp": datetime.now(timezone.utc) + timedelta(hours=3),
            "readers": [],
        }

        await collection.insert_one(new_message)

        chat_data = await collection.find_one({"msg_id": msg_id})
        if not chat_data:
            logger.error("Сообщение %s не найдено после вставки", msg_id)
            return None

        logger.info("Сообщение добавлено: %s", msg_id)
        return chat_data
    except Exception as e:
        logger.error("Ошибка при записи сообщения: %s", e, exc_info=True)
        return None


async def add_members_to_chat(
    client: AsyncIOMotorClient,
    chat_id: UUID,
    user_id: int,
    user_name: str,
    avatar: str
) -> MsgModel.Chats:
    """Добавляет пользователя в чат (или создаёт чат, если он отсутствует).

    Args:
        client (AsyncIOMotorClient): Клиент MongoDB.
        chat_id (UUID): Уникальный идентификатор чата.
        user_id (int): Идентификатор пользователя.
        user_name (str): Имя пользователя.
        avatar (str): Ссылка на аватар.

    Returns:
        MsgModel.Chats: Обновлённый объект чата.

    Raises:
        ValueError: Если чат не найден после обновления.
        Exception: При других ошибках работы с базой данных.
    """
    try:
        logger.info("Подключение к MongoDB")
        collection = client.chats_info

        new_member = {"user_id": user_id, "user_name": user_name, "avatar": avatar}

        result = await collection.update_one(
            {"chat_id": chat_id},
            {
                "$addToSet": {"members": new_member},
                "$setOnInsert": {
                    "chat_type": "simple",
                    "chat_name": None,
                    "messages": [],
                },
            },
            upsert=True,
        )
        logger.info("Добавление пользователя, matched=%s modified=%s upserted_id=%s",
                    result.matched_count, result.modified_count, getattr(result, "upserted_id", None))

        chat_data = await collection.find_one({"chat_id": chat_id})
        if not chat_data:
            raise ValueError(f"Чат {chat_id} не найден после обновления")

        chat = MsgModel.Chats(
            chat_id=chat_data["chat_id"],
            chat_type=chat_data.get("chat_type", "simple"),
            chat_name=chat_data.get("chat_name"),
            members=[
                MsgModel.Members(
                    user_id=m["user_id"],
                    user_name=m["user_name"],
                    avatar=m["avatar"],
                )
                for m in chat_data.get("members", [])
            ],
        )

        logger.info("Участник %s добавлен в чат %s", user_id, chat_id)
        return chat

    except Exception as e:
        logger.error(
            "Ошибка при добавлении участника %s в чат %s: %s",
            user_id, chat_id, e, exc_info=True
        )
        raise


async def get_chat_info(
    client: AsyncIOMotorClient,
    chat_id: UUID
) -> Optional[MsgModel.Chats]:
    """Возвращает полную информацию о чате по его ID.

    Args:
        client (AsyncIOMotorClient): Клиент MongoDB.
        chat_id (UUID): Уникальный идентификатор чата.

    Returns:
        Optional[MsgModel.Chats]: Объект чата с участниками, либо None если чат не найден.

    Raises:
        Exception: В случае ошибки работы с базой данных.
    """
    try:
        logger.info("Подключение к MongoDB для чата %s", chat_id)
        collection = client.chats_info

        chat_data = await collection.find_one({"chat_id": str(chat_id)})
        if not chat_data:
            logger.warning("Чат %s не найден в базе данных", chat_id)
            return None

        members = [
            MsgModel.Members(
                user_id=m["user_id"],
                user_name=m["user_name"],
                avatar=m["avatar"],
            )
            for m in chat_data.get("members", [])
        ]

        chat = MsgModel.Chats(
            chat_id=chat_data["chat_id"],
            chat_type=chat_data.get("chat_type", "simple"),
            chat_name=chat_data.get("chat_name"),
            members=members,
        )

        logger.info("Получен чат %s, участников: %d", chat_id, len(members))
        return chat

    except Exception as e:
        logger.error("Ошибка при получении информации по чату: %s", e, exc_info=True)
        # возвращаем None, чтобы не менять контракт
        return None


async def get_chat_id(
    client: AsyncIOMotorClient,
    current_id: int,
    user_id: int,
    chat_type: str = "simple"
):
    """Возвращает ID чата, в котором участвуют два пользователя.

    Args:
        client (AsyncIOMotorClient): Клиент MongoDB.
        current_id (int): Текущий пользователь.
        user_id (int): Второй участник.
        chat_type (str, optional): Тип чата. По умолчанию "simple".

    Returns:
        str | None: Идентификатор чата, если найден, иначе None.

    Raises:
        Exception: При ошибке поиска в базе данных.
    """
    try:
        logger.info("Поиск чата по двум участникам")
        collection = client.chats_info

        chat_data = await collection.find_one(
            {
                "members.user_id": {"$all": [user_id, current_id]},
                "chat_type": chat_type,
            }
        )

        if chat_data:
            logger.info("Найден чат %s", chat_data.get("chat_id"))
            return chat_data["chat_id"]
        return None
    except Exception as e:
        logger.error("Ошибка при поиске чата: %s", e, exc_info=True)
        raise


async def get_messages(
    client: AsyncIOMotorClient,
    chat_id: str,
    limit: int,
    offset: int
):
    """Возвращает список сообщений чата с пагинацией.

    Args:
        client (AsyncIOMotorClient): Клиент MongoDB.
        chat_id (str): Идентификатор чата.
        limit (int): Максимальное количество сообщений.
        offset (int): Смещение для пагинации.

    Returns:
        list[dict]: Список сообщений в формате словарей.

    Raises:
        Exception: В случае ошибки чтения из базы данных.
    """
    try:
        collection = client.chats_msgs

        cursor = (
            collection.find({"chat_id": chat_id})
            .sort("timestamp", -1)
            .skip(offset)
            .limit(limit)
        )

        message_list = []
        async for m in cursor:
            try:
                readers = [
                    {
                        "user_id": r["user_id"],
                        "user_name": r["user_name"],
                        "avatar": r.get("avatar"),
                    }
                    for r in m.get("readers", [])
                    if _valid_reader(r)
                ]

                message = {
                    "msg_id": str(m["msg_id"]),
                    "chat_id": str(m["chat_id"]),
                    "content": m.get("content"),
                    "sender_id": int(m["sender_id"]),
                    "timestamp": _iso(m.get("timestamp")),
                    "readers": readers,
                }

                # Валидация через Pydantic модель
                _ = MsgModel.Messages(**message)
                message_list.append(message)

            except Exception as doc_error:
                logger.error("Ошибка обработки документа: %s", doc_error, exc_info=True)
                continue

        return message_list

    except Exception as e:
        logger.error("Ошибка при получении сообщений: %s", e, exc_info=True)
        raise
#endregion