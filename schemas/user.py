from pydantic import BaseModel
from typing import Optional

class WhoAmI(BaseModel):
    """Модель, описывающая текущего авторизованного пользователя.

    Attributes:
        user_id (Optional[int]): Уникальный идентификатор пользователя.
        username (Optional[str]): Логин или имя пользователя.
        avatar (Optional[str]): Ссылка на аватар пользователя.
    """

    user_id: Optional[int] = None
    username: Optional[str] = None
    avatar: Optional[str] = None


class User(BaseModel):
    """Модель пользователя (краткое представление).

    Attributes:
        id (int): Уникальный идентификатор пользователя.
        name (str): Отображаемое имя пользователя.
        avatar (Optional[str]): Ссылка на аватар пользователя.
    """

    id: int
    name: str
    avatar: Optional[str]
