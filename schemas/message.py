from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Members(BaseModel):
    """Модель участника чата.

    Attributes:
        user_id (int): Уникальный идентификатор пользователя.
        user_name (str): Имя пользователя (отображаемое).
        avatar (Optional[str]): Ссылка на аватар пользователя.
    """

    user_id: int
    user_name: str
    avatar: Optional[str] = None


class Messages(BaseModel):
    """Модель сообщения в чате.

    Attributes:
        msg_id (str): Уникальный идентификатор сообщения.
        chat_id (str): Идентификатор чата, к которому относится сообщение.
        content (Optional[str]): Текстовое содержимое сообщения.
        sender_id (int): Идентификатор отправителя.
        timestamp (datetime): Время отправки сообщения (UTC).
        readers (List[Members]): Список участников, которые прочитали сообщение.
    """

    msg_id: str
    chat_id: str
    content: Optional[str]
    sender_id: int
    timestamp: datetime
    readers: List[Members]


class Chats(BaseModel):
    """Модель чата.

    Attributes:
        chat_id (str): Уникальный идентификатор чата.
        chat_type (str): Тип чата (по умолчанию 'simple').
        chat_name (Optional[str]): Название чата (для групповых).
        members (List[Members]): Список участников чата.
    """

    chat_id: str
    chat_type: str = "simple"
    chat_name: Optional[str] = None
    members: List[Members]
