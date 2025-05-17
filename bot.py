import os
import asyncio
import logging

from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties

from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from dotenv import load_dotenv

# 1) .env faylini yuklash
load_dotenv()

# ========= SQLAlchemy sozlamalari =========
DATABASE_URL = "sqlite:///users.db"
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)
# ==========================================

# ========= Bot sozlamalari =========
# 2) Token va WebApp URL ni .env dan o‘qish
BOT_TOKEN   = os.getenv("BOT_TOKEN")
WEBAPP_URL  = os.getenv("WEBAPP_URL")

if not BOT_TOKEN or not WEBAPP_URL:
    raise RuntimeError("Iltimos, .env faylida BOT_TOKEN va WEBAPP_URL ni to‘g‘ri sozlang!")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)
# ======================================

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    telegram_id = message.from_user.id
    first = message.from_user.first_name or ""
    last = message.from_user.last_name or ""
    full_name = f"{first} {last}".strip()

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            user = User(telegram_id=telegram_id, full_name=full_name)
            db.add(user)
            db.commit()
            logging.info(f"Yangi foydalanuvchi qo‘shildi: {telegram_id} — {full_name}")
        else:
            logging.info(f"Foydalanuvchi allaqachon mavjud: {telegram_id}")
    except Exception as e:
        logging.error(f"DB xato: {e}")
        db.rollback()
    finally:
        db.close()

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔢 Hisoblash")]],
        resize_keyboard=True,
        input_field_placeholder="Hisoblashni tanlang"
    )
    await message.answer(
        f"Assalomu alaykum, {full_name}!\nQuyidagi tugma orqali elektr hisoblash ilovasini oching:",
        reply_markup=keyboard
    )

@router.message(F.text == "🔢 Hisoblash")
async def send_webapp_button(message: Message):
    inline_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="⚡️ Web ilovani ochish",
                    web_app=WebAppInfo(url=WEBAPP_URL)
                )
            ]
        ]
    )
    await message.answer("⬇️ Tugmani bosing va hisoblash ilovasini oching:", reply_markup=inline_kb)

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
