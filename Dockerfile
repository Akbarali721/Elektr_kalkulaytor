# 1. Python-базовый образ
FROM python:3.11-slim

# 2. Рабочая директория
WORKDIR /app

# 3. Устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Копируем весь код
COPY . .

# 5. Открываем порт (совпадает с $PORT из fly.toml)
EXPOSE 8080

# 6. ENTRYPOINT в shell-форме, чтобы $PORT разворачивался правильно
ENTRYPOINT sh -c "uvicorn main:app --host 0.0.0.0 --port \$PORT"
