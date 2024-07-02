from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import datetime
import calendar

async def create_calendar(year=None, month=None, day_start=None, prev_disable=False):
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
                if day_start is not None and day_start > day:
                    row.append(InlineKeyboardButton(" ", callback_data=skip_button))
                else:
                    row.append(InlineKeyboardButton(str(day), callback_data=callback_format("DAY", year, month, day)))
        keyboard.append(row)
    
    row = []
    if prev_disable:
        row.append(InlineKeyboardButton(" ", callback_data=skip_button))
    else:
        row.append(InlineKeyboardButton("⏪", callback_data=callback_format("PREV", year, month, day)))
    row.append(InlineKeyboardButton("❌", callback_data=callback_format("CLOSE", year, month, day)))
    row.append(InlineKeyboardButton("⏩", callback_data=callback_format("NEXT", year, month, day)))
    keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def callback_format(action, year, month, day):
    return f"{action}|{str(year)}|{str(month)}|{str(day)}"

async def inline_calendar_handler(update, context):
    query = update.callback_query
    (action, year, month, day) = query.data.split("|")
    first_day = datetime.datetime(int(year), int(month), 1)
    return_data = (False, None)
    if action == "SKIP":
        await context.bot.answer_callback_query(callback_query_id=query.id)
    elif action == "DAY":
        date = datetime.datetime(int(year), int(month), int(day))
        await context.bot.edit_message_text(text = query.message.text,
                                            chat_id = query.message.chat_id,
                                            message_id = query.message.message_id)
        return_data = True, datetime.datetime(int(year), int(month), int(day))
    elif action == "PREV":
        date_pre = first_day - datetime.timedelta(days=1)
        await context.bot.edit_message_text(text=query.message.text,
                                            chat_id = query.message.chat_id,
                                            message_id = query.message.message_id,
                                            reply_markup = await create_calendar(int(date_pre.year), int(date_pre.month)))
    elif action == "NEXT":
        date_next = first_day + datetime.timedelta(days=31)
        await context.bot.edit_message_text(text=query.message.text,
                                            chat_id = query.message.chat_id,
                                            message_id = query.message.message_id,
                                            reply_markup = await create_calendar(int(date_next.year), int(date_next.month)))
    elif action == "CLOSE":
        await context.bot.delete_message(chat_id = query.message.chat_id, message_id = query.message.message_id)
    else:
        await context.bot.answer_callback_query(callback_query_id=query.id, text="알 수 없는 명령입니다.")
    return return_data
