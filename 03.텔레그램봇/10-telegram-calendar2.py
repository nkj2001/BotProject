from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, Application
from dotenv import load_dotenv
import os
import logging
from modules import telcalendar

load_dotenv()
TOKEN = os.getenv("TOKEN")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_calendar(update, context):
    await update.message.reply_text(text="날짜를 선택하세요", reply_markup=await telcalendar.create_calendar())

async def inline_calendar_handler(update, context):
    selected, date = await telcalendar.inline_calendar_handler(update, context)
    if selected:
        await context.bot.send_message(chat_id=update.callback_query.from_user.id, text=str(date.strftime("%Y-%m-%d")))

application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("cal", create_calendar))
application.add_handler(CallbackQueryHandler(inline_calendar_handler))
application.run_polling(allowed_updates=Update.ALL_TYPES)