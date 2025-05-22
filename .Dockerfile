FROM python:3.12

WORKDIR /app

ENV REDIS_HOST="prod.redis.b.aovzerk.ru"
ENV REDIS_PORT=6379
ENV REDIS_PASSWORD="AKJfgqweytYoafy123123w"

#mongo
ENV MONGO_URL="mongodb://user1:KJAJHjkafhg123KJASHDhasdf@mongo.b.aovzerk.ru:27017"

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
