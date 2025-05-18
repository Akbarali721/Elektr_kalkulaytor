# 1. Python asosli tasvir
FROM python:3.11-slim

# 2. Ishlash papkasiga o‘tamiz
WORKDIR /app

# 3. Talablarni o‘rnatamiz
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Kodni nusxalaymiz
COPY . .

# 5. Portni e’lon qilamiz
EXPOSE 8000

# 6. Ishga tushirish buyrug‘i (Fly’da PORT muhit o‘zgaruvchisiga e’tibor!)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]