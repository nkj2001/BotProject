from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, MessageHandler, filters
from dotenv import load_dotenv
import os
import logging
import cv2
from uuid import uuid4

load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = 123456789
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def filter_image(update, context):
    if len(update.message.photo) > 0:
        file = await context.bot.get_file(update.message.photo[-1].file_id)
        filename = f"{str(uuid4())}.jpg"
        await file.download_to_drive(filename)
        keyboard = [
            [
                InlineKeyboardButton("그레이", callback_data=f"G{filename}"),
                InlineKeyboardButton("축소", callback_data=f"S{filename}"),
                InlineKeyboardButton("아무작업도안함", callback_data=f"X{filename}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("이미지 효과를 선택하세요: ", reply_markup=reply_markup)

async def callback_button(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    effect = query.data[0:1]
    filename = query.data[1:]
    query.delete_message()
    if effect == "G":
        cv_image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        img_bytes = cv2.imencode(".jpg", cv_image)[1]
        await context.bot.send_photo(chat_id=chat_id, photo=bytes(img_bytes), write_timeout=6000)
    elif effect == "S":
        cv_image = cv2.imread(filename, cv2.IMREAD_COLOR)
        resize_image = cv2.resize(cv_image, dsize=(0, 0), fx=0.5, fy=0.5)
        img_bytes = cv2.imencode(".jpg", resize_image)[1]
        await context.bot.send_photo(chat_id=chat_id, photo=bytes(img_bytes), write_timeout=6000)
    os.unlink(filename)
    
application = Application.builder().token(TOKEN).build()
application.add_handler(MessageHandler(filters.PHOTO, filter_image))
application.add_handler(CallbackQueryHandler(callback_button))
application.run_polling(allowed_updates=Update.ALL_TYPES)
