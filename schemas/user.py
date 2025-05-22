from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import date

class WhoAmI(BaseModel):
    user_id: Optional[int] = None
    username: Optional[str] = None
    avatar: Optional[str] = None

class User(BaseModel):
    id: int
    name: str
    avatar: Optional[str]
