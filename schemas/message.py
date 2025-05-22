from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from typing import List
from fastapi import WebSocket


class Members(BaseModel):
    user_id : int
    user_name : str
    avatar : Optional[str]= None

class Messages(BaseModel):
    msg_id : str
    chat_id: str
    content : Optional[str]
    sender_id : int
    timestamp : datetime
    readers : List[Members]


class Chats(BaseModel):
    chat_id: str
    chat_type: str = 'simple'
    chat_name: Optional[str] = None
    members : List[Members]