from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, CallbackContext, Application, ConversationHandler, filters, MessageHandler
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

async def join_start(update, context):
    reply_keyboard =[
        ["남자", "여자"]
    ]
    context.user_data["join"] = {}
    await update.message.reply_text(
        "가입절차를 중지하고 싶으면 언제든 /joinout을 입력하시면 됩니다.\n\n"
        "먼저 당신은 '남자' 인지 '여자' 인지 선택해주세요.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True, input_field_placeholder="남자? 여자?"
        )
    )
    return GENDER

async def join_gender(update, context):
    context.user_data["join"].update({"gender": update.message.text})
    await update.message.reply_text(
        "이제 이름을 입력해주세요\n"
        "이름은 2자이상 4글자까지만 입력됩니다.",
        reply_markup=ReplyKeyboardRemove()
    )
    return NAME

async def join_name(update, context):
    context.user_data["join"].update({"name": update.message.text})
    await update.message.reply_text(
        "나이를 입력해주세요\n"
        "나이는 숫자로만 입력하세요",
    )
    return AGE

async def join_age(update, context):
    context.user_data["join"].update({"age": update.message.text})
    await update.message.reply_text(
        "연락처를 입력해주세요\n"
        "연락처는 xxx-xxxx-xxxx 형태로 입력하세요"
    )
    return TEL

async def join_tel(update, context):
    context.user_data["join"].update({"tel": update.message.text})
    await update.message.reply_text(
        "가입을 축하드립니다~!!\n"
        f"{context.user_data['join']}"
    )
    del context.user_data["join"]
    return ConversationHandler.END

async def join_out(update, context):
    del context.user_data["join"]
    await update.message.reply_text(
        "가입을 중단합니다",
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

GENDER, NAME, AGE, TEL = range(4)
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("join", join_start)],
    states={
        GENDER: [MessageHandler(filters.Regex(r'^(남자|여자)$'), join_gender)],
        NAME: [MessageHandler(filters.Regex(r'^[가-힣]{2,4}$'), join_name)],
        AGE: [MessageHandler(filters.Regex(r'^[0-9]{1,3}$'), join_age)],
        TEL: [MessageHandler(filters.Regex(r'^\d{3}-\d{3,4}-\d{4}$'), join_tel)]
    },
    fallbacks=[CommandHandler("joinout", join_out)]
)

application = Application.builder().token(TOKEN).build()
application.add_handler(conv_handler)
application.run_polling(allowed_updates=Update.ALL_TYPES)