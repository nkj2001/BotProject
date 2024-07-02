from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, Application
from dotenv import load_dotenv
import os
import logging
import datetime
import calendar
load_dotenv()
TOKEN = os.getenv("TOKEN")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def create_calendar(update, context):
    year = None
    month = None
    now = datetime.datetime.now()
    year = now.year if year is None else year
    month = now.month if month is None else month
    keyboard = []
    row = []
    skip_button = callback_format("SKIP", year, month, 0)
    row.append(InlineKeyboardButton(f"{year}년 {month}월", callback_data=skip_button))
    keyboard.append(row)
    row = []
    for day in ["일", "월", "화", "수", "목", "금", "토"]:
        row.append(InlineKeyboardButton(day, callback_data=skip_button))
    keyboard.append(row)
    calendar.setfirstweekday(6)
    my_calendar = calendar.monthcalendar(year, month)

    for week in my_calendar:
        row = []
        for day in week:
            if day == 0:
                row.append(InlineKeyboardButton(" ", callback_data=skip_button))
            else:
                row.append(InlineKeyboardButton(str(day), callback_data=callback_format("DAY", year, month, day)))
        keyboard.append(row)
    
    row = []
    row.append(InlineKeyboardButton("⏪", callback_data=callback_format("PREV", year, month, day)))
    row.append(InlineKeyboardButton("❌", callback_data=callback_format("CLOSE", year, month, day)))
    row.append(InlineKeyboardButton("⏩", callback_data=callback_format("NEXT", year, month, day)))
    keyboard.append(row)
    
    await update.message.reply_text(text="날짜를 선택하세요", reply_markup=InlineKeyboardMarkup(keyboard))

def callback_format(action, year, month, day):
    return f"{action}|{str(year)}|{str(month)}|{str(day)}"

async def inline_calendar_handler(update, context):
    query = update.callback_query
    (action, year, month, day) = query.data.split("|")
    if action == "SKIP":
        await context.bot.answer_callback_query(callback_query_id=query.id)
    elif action == "DAY":
        date = datetime.datetime(int(year), int(month), int(day))
        await context.bot.edit_message_text(text = query.message.text,
                                            chat_id = query.message.chat_id,
                                            message_id = query.message.message_id)
        await context.bot.send_message(chat_id = update.callback_query.from_user.id, text=str(date.strftime("%Y-%m-%d")))
    elif action == "PREV":
        pass
    elif action == "NEXT":
        pass
    elif action == "CLOSE":
        await context.bot.delete_message(chat_id = query.message.chat_id, message_id = query.message.message_id)

application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("calendar", create_calendar))
application.add_handler(CallbackQueryHandler(inline_calendar_handler))
application.run_polling(allowed_updates=Update.ALL_TYPES)