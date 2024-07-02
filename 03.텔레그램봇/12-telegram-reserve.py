from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, Application, filters, MessageHandler, ConversationHandler
from dotenv import load_dotenv
import os
import logging
from modules import google_calendar
from modules import telcalendar
from datetime import datetime, timedelta

load_dotenv()
TOKEN = os.getenv("TOKEN")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

R_START, R_FULL, R_TIME, R_MEMO, R_NAME, R_TEL = range(6)

async def res_start(update, context):
    now = datetime.now()
    await update.message.reply_text(text="날짜를 선택하세요", reply_markup=await telcalendar.create_calendar(day_start=now.day, prev_disable=True))
async def res_full(update, context):
    input_data = update.message.text
    context.user_data["reserve"] = None
    if input_data == "예약종료":
        await update.message.reply_text("예약 종료", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    else:
        now = datetime.now()
        await update.message.reply_text(text="날짜를 선택하세요", reply_markup=await telcalendar.create_calendar(day_start=now.day, prev_disable=True))
        return R_START
async def res_receive_time(update, context):
    user_data = context.user_data["reserve"]
    date = user_data.get("date")
    input_date = update.message.text
    _hour, _min = input_date.split(":")
    date = date.replace(hour=int(_hour), minute=int(_min))
    events = google_calendar.get_calendar_events(date - timedelta(minutes=20), date + timedelta(minutes=20))
    if len(events) > 0:
        reply_keyboard = [['계속', '예약종료']]
        reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=False, one_time_keyboard=True)
        msg = f"죄송합니다.\n{date.year}년 {date.month}월 {date.day}일 {_hour}시 예약이 꽉 찼습니다.\n"
        msg += "다른 날짜를 선택하시려면 계속 버튼을 클릭하세요."
        await context.bot.send_message(chat_id=update.message.chat_id, text=msg, reply_markup=reply_markup)
        return R_FULL
    else:
        msg = f"{date.year}년 {date.month}월 {date.day}일 {date.hour}시 예약입니다\n"
        msg += "에약자 성함을 입력해주세요."
        msg += "이름은 2자~4자 까지만 입력됩니다."
        context.user_data["reserve"].update({"date": date})
        await context.bot.send_message(chat_id=update.message.chat_id, text=msg)
        return R_NAME
async def res_receive_memo(update, context):
    user_data = context.user_data["reserve"]
    input_data = update.message.text
    user_data.update(
        {"memo": input_data, "user_id": update.message.from_user.id}
    )
    msg = res_complete(user_data)
    await context.bot.send_message(chat_id=update.message.chat_id, text=msg)
    return ConversationHandler.END

def res_complete(user_data):
    msg = f'{user_data.get("name")}님 예약 현황\n'
    msg += f'예약 일자 : {user_data.get("date")}\n'
    msg += f'연락처 : {user_data.get("tel")}\n'

    memo = f'{str(user_data.get("user_id"))}\n'
    memo += str(user_data.get("tel"))
    if user_data.get("memo"):
        msg += f'예약메모 : {user_data.get("memo")}\n'
        memo += f"\n{user_data.get("memo")}"
    msg += "\n예약해 주셔서 감사합니다."

    google_calendar.insert_event(summary=f'{user_data.get("name")}님 예약',
                                 start_date=user_data.get("date"),
                                 end_date=user_data.get("date") + timedelta(hours=1),
                                 description=memo)
    return msg

async def res_receive_memo_skip(update, context):
    user_data = context.user_data["reserve"]
    user_data.update({
        "user_id": update.message.from_user.id
    })
    msg = res_complete(user_data)
    await context.bot.send_message(chat_id=update.message.chat_id, text=msg)
    return ConversationHandler.END
async def res_receive_name(update, context):
    input_data = update.message.text
    context.user_data["reserve"].update({"name": input_data})
    msg = f"예약자 성함 : {input_data}님 확인 되었습니다.\n"
    msg += "이제 예약자님과 연락 가능한 연락처를 입력해주세요\n"
    msg += "연락처는 <code>010-xxx-xxxx</code> 형식으로 입력해주세요."
    await context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode="HTML")
    return R_TEL
async def res_receive_tel(update, context):
    user_name = context.user_data["reserve"].get("name")
    input_data = update.message.text
    context.user_data["reserve"].update({"tel": input_data})
    msg = f"예약자 성함: {user_name}님 확인 되었습니다.\n"
    msg += f"예약자 연락처: {input_data} 확인 되셨습니다.\n"
    msg += "혹시 예약에 추가로 남기실 메모가 있으세요?\n"
    msg += "남기실 메모가 없으시면 /skip 을 입력하세요"
    await context.bot.send_message(chat_id=update.message.chat_id, text=msg, parse_mode="HTML")
    return R_MEMO
async def res_end(update, context):
    await update.message.reply_text("예약 종료", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

async def inline_calendar_handler(update, context):
    selected, date = await telcalendar.inline_calendar_handler(update, context)
    if selected:
        e_date = date + timedelta(hours=23)
        events = google_calendar.get_calendar_events(timeMin=date, timeMax=e_date)
        await context.bot.delete_message(chat_id=update.callback_query.message.chat_id, message_id=update.callback_query.message.message_id)
        if len(events) >= 5:
            reply_keyboard = [['계속', '예약종료']]
            reply_markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=False, one_time_keyboard=True)
            msg = f"죄송합니다.\n{date.year}년 {date.month}월 {date.day}일 예약이 꽉 찼습니다.\n"
            msg += "다른 날짜를 선택하시려면 계속 버튼을 클릭하세요."
            await context.bot.send_message(chat_id=update.callback_query.message.chat_id, text=msg, reply_markup=reply_markup)
            return R_FULL
        else:
            context.user_data["reserve"] = {"date": date}
            await context.bot.send_message(chat_id=update.callback_query.from_user.id,
                                           text=f"{date.year}년 {date.month}월 {date.day}일 몇시에 예약 할까요?\n시간은 17:00 형식으로 입력해주세요.")
            return R_TIME

conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("reserve", res_start),
        CallbackQueryHandler(inline_calendar_handler)
    ],
    states={
        R_START: [
            CommandHandler("reserve", res_start),
            CallbackQueryHandler(inline_calendar_handler)
        ],
        R_FULL: [MessageHandler(filters.Regex(r"^(계속|예약종료)$"), res_full)],
        R_TIME: [MessageHandler(filters.Regex(r"^\d{2}\:\d{2}$"), res_receive_time)],
        R_MEMO: [
            MessageHandler(filters.TEXT & ~filters.COMMAND, res_receive_memo),
            CommandHandler('skip', res_receive_memo_skip)
        ],
        R_NAME: [MessageHandler(filters.Regex(r"^[가-힣]{2,4}$"), res_receive_name)],
        R_TEL: [MessageHandler(filters.Regex(r"^\d{3}\-\d{3,4}\-\d{4}$"), res_receive_tel)],
    },
    fallbacks=[CommandHandler("end_reserve", res_end)]
)

application = Application.builder().token(TOKEN).build()
application.add_handler(conv_handler)
application.run_polling(allowed_updates=Update.ALL_TYPES)