from locust import HttpUser, task, between
import random
from src import concts as c
CHAT_SERVICE_PREFIX = c.PATH_PREFIX

class ChatServiceUser(HttpUser):
    wait_time = between(0.2, 1.0)

    def on_start(self):
        #имитация авторизованного пользователя
        self.client.headers.update({"Accept": "application/json"})

    @task(2)
    def list_chats(self):
        self.client.get(f"{CHAT_SERVICE_PREFIX}/wss/chats")

    @task(3)
    def create_chat(self):
        username = random.choice(["alice", "bob", "carol", "dave"])
        self.client.post(f"{CHAT_SERVICE_PREFIX}/wss/create_chat", params={"username": username})

    @task(5)
    def get_messages(self):
        chat_id = "8ed765ff-5b78-4801-b202-7eb5a7d77dac"
        self.client.get(f"{CHAT_SERVICE_PREFIX}/wss/chat_messages/{chat_id}", params={"offset": 0, "limit": 20})
