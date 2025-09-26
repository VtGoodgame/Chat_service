# tests/unit/test_mongo.py
import pytest
from unittest.mock import AsyncMock
from uuid import uuid4
from datetime import datetime, timezone, timedelta

from db import mongo as MongoDB


@pytest.mark.asyncio
async def test_add_message_mongo_inserts_and_returns_document():
    chat_id = "9af4e8dd-8954-4972-b9db-ebfb44f2371e"
    sender_id = 1
    content = "unit test message"

    mock_collection = AsyncMock()
    mock_collection.insert_one = AsyncMock(return_value=None)
    inserted = {
        "msg_id": "09cf81ce-89ae-4767-b33b-a3234388c897",
        "chat_id": chat_id,
        "content": content,
        "sender_id": sender_id,
        "timestamp": datetime.now(timezone.utc) + timedelta(hours=3),
        "readers": [],
    }
    mock_collection.find_one = AsyncMock(return_value=inserted)

    mock_client = AsyncMock()
    mock_client.chats_msgs = mock_collection

    result = await MongoDB.add_message_mongo(
        mock_client, chat_id=chat_id, sender_id=sender_id, content=content
    )

    mock_collection.insert_one.assert_awaited()
    mock_collection.find_one.assert_awaited()
    assert result["chat_id"] == chat_id
    assert result["content"] == content
    assert result["sender_id"] == sender_id


@pytest.mark.asyncio
async def test_get_chat_info_returns_model():
    chat_id = str(uuid4())
    #Документ, как его вернула бы MongoDB
    doc = {
        "chat_id": chat_id,
        "chat_type": "simple",
        "chat_name": None,
        "members": [{"user_id": 1, "user_name": "Vtgoodgame", "avatar": ""}],
    }

    mock_collection = AsyncMock()
    mock_collection.find_one = AsyncMock(return_value=doc)
    mock_client = AsyncMock()
    mock_client.chats_info = mock_collection

    chat = await MongoDB.get_chat_info(mock_client, chat_id)
    assert chat is not None
    assert chat.chat_id == chat_id
    assert chat.members[0].user_name == "alice"


@pytest.mark.asyncio
async def test_get_chat_id_filters_by_members_and_type():
    mock_collection = AsyncMock()
    mock_collection.find_one = AsyncMock(return_value={"chat_id": "9af4e8dd-8954-4972-b9db-ebfb44f2371e"})
    mock_client = AsyncMock()
    mock_client.chats_info = mock_collection

    chat_id = await MongoDB.get_chat_id(mock_client, current_id=1, user_id=2, chat_type="simple")
    assert chat_id == "9af4e8dd-8954-4972-b9db-ebfb44f2371e"
    mock_collection.find_one.assert_awaited_with(
        {"members.user_id": {"$all": [2, 1]}, "chat_type": "simple"}
    )
