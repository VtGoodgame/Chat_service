FROM python:3.12

WORKDIR /app

ENV REDIS_HOST=""
ENV REDIS_PORT
ENV REDIS_PASSWORD=""

#mongo
ENV MONGO_URL=""

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
