import pytest
from unittest.mock import patch, AsyncMock
import httpx
from main import app


@pytest.mark.asyncio
async def test_socket_get_chats_endpoint_lists_chats():
    with patch("src.auth.whoami", new=lambda: None):
        pass  #чтобы не ругался на отсутствие авторизации

    async def fake_whoami():
        class U:
            user_id = 1
            username = "Vtgoodgame"
            avatar = ""
        return U()

    #Мокаем зависимость auth.whoami и get_mongo_db
    with patch("main.auth.whoami", new=fake_whoami), \
         patch("main.get_mongo_db") as get_db:

        fake_db = AsyncMock()
        fake_db.chats_info.find.return_value.to_list = None
        #отдаём один чат через async-итерирование
        class FakeCursor:
            def __aiter__(self):
                doc = {
                    "chat_id": "8ed765ff-5b78-4801-b202-7eb5a7d77dac",
                    "chat_type": "simple",
                    "chat_name": None,
                    "members": [{"user_id": 1, "user_name": "Vtgoodgame", "avatar": ""}],
                }
                async def gen():
                    yield doc
                return gen()

        fake_db.chats_info.find.return_value = FakeCursor()
        get_db.return_value = fake_db

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as ac:
            resp = await ac.get("/api/chat-service/wss/chats")
            assert resp.status_code == 200
            data = resp.json()
            assert isinstance(data, list)
            assert data[0]["chat_id"] == "8ed765ff-5b78-4801-b202-7eb5a7d77dac"


@pytest.mark.asyncio
async def test_create_chat_with_user_creates_when_not_exists():
    #Подменяем auth.whoami
    async def fake_whoami():
        class U:
            user_id = 1
            username = "Vtgoodgame"
            avatar = ""
        return U()

    #Мокаем зависимости
    with patch("main.auth.whoami", new=fake_whoami), \
         patch("main.check_user_blocked_by_username", new=AsyncMock(return_value={"blocked_by_user": False, "you_blocked_user": False})), \
         patch("main.MongoDB.get_chat_id", new=AsyncMock(return_value=None)), \
         patch("main.MongoDB.add_members_to_chat", new=AsyncMock()), \
         patch("main.MongoDB.get_chat_info") as mock_get_chat_info, \
         patch("httpx.AsyncClient.get") as mock_get:

        #вернёт target user
        mock_get.return_value.__aenter__.return_value = None 
        async def fake_async_get(url, params=None, timeout=None):
            class Resp:
                status_code = 200
                def json(self):
                    return {"id": 2, "username": "kasada", "avatar": ""}
            return Resp()
        mock_get.side_effect = fake_async_get

        #Возвращаем финальную информацию о чате
        class Chat:
            chat_id = "9af4e8dd-8954-4972-b9db-ebfb44f2371e"
            chat_type = "simple"
            chat_name = None
            members = []
        mock_get_chat_info.return_value = Chat()

        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=app), base_url="http://test"
        ) as ac:
            resp = await ac.post("/api/chat-service/wss/create_chat", params={"username": "kasada"})
            assert resp.status_code == 200
            assert resp.json()["chat_id"] == "9af4e8dd-8954-4972-b9db-ebfb44f2371e"