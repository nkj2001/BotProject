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

async def cal(update, context):
    reply_keyboard = [
        ['1', '2', '3', '*'],
        ['4', '5', '6', '/'],
        ['7', '8', '9', '-'],
        ['0', '.', '=', '+']
    ]
    reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True, one_time_keyboard=False)
    context.user_data['last_message'] = await context.bot.send_message(text='0', chat_id=update.message.chat_id)
    await update.message.reply_text("계산식을 입력하세요 종료는 /cancel: ", reply_markup=reply_markup)
    return NUMBER

async def number(update, context):
    last_message = context.user_data['last_message']
    old_val = last_message.text
    await context.bot.delete_message(str(update.message.chat_id), str(update.message.message_id))
    if update.message.text.strip() == "=":
        context.user_data["last_message"] = await context.bot.edit_message_text(
                                                text = str(eval(old_val)),
                                                chat_id = last_message.chat_id,
                                                message_id = last_message.message_id
                                            )
    else:
        new_val = f"{update.message.text}" if old_val == "0" else f"{old_val}{update.message.text}"
        context.user_data["last_message"] = await context.bot.edit_message_text(
                                                text=f"{new_val}",
                                                chat_id=last_message.chat_id,
                                                message_id=last_message.message_id
                                            )
    return NUMBER
            

async def end_cal(update, context):
    update.message.reply_text("계산기 종료", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

NUMBER = range(1)
conv_handler = ConversationHandler(
    entry_points=[CommandHandler("cal", cal)],
    states={
        NUMBER: [MessageHandler(filters.Regex(r"^[0-9|(\+|\-|\*|\/|\=|\.)]$"), number)]
    },
    fallbacks=[CommandHandler("cancel", end_cal)]
)

application = Application.builder().token(TOKEN).build()
application.add_handler(conv_handler)
application.run_polling(allowed_updates=Update.ALL_TYPES)