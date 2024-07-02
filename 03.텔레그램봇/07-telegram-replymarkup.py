from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, ContextTypes, CommandHandler, CallbackQueryHandler, CallbackContext
from dotenv import load_dotenv
import os
import logging
import requests
from uuid import uuid4

load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = 123456789
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def show_button(update, context):
    keyboard = [
        [
            InlineKeyboardButton("버튼1", callback_data="1"),
            InlineKeyboardButton("버튼2", callback_data="2"),
            InlineKeyboardButton("버튼3", callback_data="3"),
        ],
        [
            InlineKeyboardButton("버튼A", callback_data="A"),
            InlineKeyboardButton("버튼B", callback_data="B"),
            InlineKeyboardButton("버튼C", callback_data="C"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("버튼을 선택하세요:", reply_markup=reply_markup)

async def show_urls(update, context):
    keyboard = [
        [
            InlineKeyboardButton("네이버", url="https://www.naver.com"),
            InlineKeyboardButton("구글", url="https://www.google.com"),
            InlineKeyboardButton("다음", url="https://www.daum.net"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("링크를 선택하세요:", reply_markup=reply_markup)

async def callback_button(update, context):
    query = update.callback_query
    #await query.answer(query.data, show_alert=True)
    await query.edit_message_text(text=f"선택한 버튼은 : {query.data}")

application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("button", show_button))
application.add_handler(CommandHandler("urls", show_urls))
application.add_handler(CallbackQueryHandler(callback_button))
application.run_polling(allowed_updates=Update.ALL_TYPES)
