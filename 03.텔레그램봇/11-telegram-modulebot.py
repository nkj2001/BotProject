from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, CallbackContext, CallbackQueryHandler, Application, filters, MessageHandler, ConversationHandler
from dotenv import load_dotenv
import os
import logging
from modules import money_exchange_rate
from modules import weather
from modules import qrcode
import cv2
import numpy as np

load_dotenv()
TOKEN = os.getenv("TOKEN")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def exchange(update, context):
    value = update.message.text
    value = "".join(value.split(" "))
    r = money_exchange_rate.google_money_exchange_rate(value)
    output = f"{r[1]} {r[0]}" if r[-1] is not None else "환율 데이터가 없습니다"
    await update.message.reply_text(output)

async def show_weather(update, context):
    value = update.message.text.replace("날씨", "").strip()
    r = weather.get_weather(value)
    output = ""
    for k, v in r.items():
        output += f"{k}: {v}\n"
    await update.message.reply_text(output)

async def qr_start(update, context):
    keyboard = [
        [
            InlineKeyboardButton("QRCODE 생성", callback_data="encode"),
            InlineKeyboardButton("QRCODE 분석", callback_data="decode"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("버튼을 선택하세요", reply_markup=reply_markup)

async def inline_qr_handler(update, context):
    query = update.callback_query
    data = query.data
    if data == "encode":
        await query.edit_message_text(text="변환할 데이터를 입력하세요")
        return QR_ENCODE
    else:
        await query.edit_message_text(text="이미지를 업로드 하세요")
        return QR_DECODE

async def qr_encode(update, context):
    text = update.message.text
    filepath = qrcode.QRCreater().make(text).png()
    await context.bot.send_photo(chat_id=update.message.chat_id, photo=open(filepath, "rb"), write_timeout=6000)
    os.unlink(filepath)
    return ConversationHandler.END

async def qr_decode_photo(update, context):
    if len(update.message.photo) > 0:
        msg = "QRCode 분석을 위한 이미지는 Image 형식으로 보내야합니다"
        await context.bot.send_message(chat_id=update.message.chat_id, text=msg)
        return QR_DECODE

async def qr_decode_document(update, context):
    file_id = update.message.document.file_id
    file = await context.bot.get_file(file_id)
    image_bytes = bytes(await file.download_as_bytearray())
    cv_image = cv2.imdecode(np.frombuffer(image_bytes, np.uint8), -1)
    results = qrcode.read_qrcode_zbar(cv_image)
    output = ""
    for r in results:
        _data = r.get("data")
        _type = r.get("type")
        output += f"{_data} : {_type}\n"
    await context.bot.send_message(chat_id=update.message.chat_id, text=output, disable_web_page_preview=True)
    return ConversationHandler.END

async def qr_end(update, context):
    await update.message.reply_text("QRCode 종료", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

QR_ENCODE, QR_DECODE = range(2)
qr_conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler("qrcode", qr_start),
        CallbackQueryHandler(inline_qr_handler)
    ],
    states={
        QR_ENCODE : [MessageHandler(filters.TEXT & ~filters.COMMAND, qr_encode)],
        QR_DECODE : [
            MessageHandler(filters.PHOTO, qr_decode_photo),
            MessageHandler(filters.Document.ALL, qr_decode_document),
        ]
    },
    fallbacks=[CommandHandler('qrend', qr_end)]
)
filter_exchange = filters.Regex(r"^[0-9]+\s*(유로|엔|달러|달라|위안|홍콩달라|홍콩달러)$")
filter_weather = filters.Regex(r"^[가-힣]+\s*날씨$")
application = Application.builder().token(TOKEN).build()
application.add_handler(MessageHandler(filter_exchange, exchange))
application.add_handler(MessageHandler(filter_weather, show_weather))
application.add_handler(qr_conv_handler)
application.run_polling(allowed_updates=Update.ALL_TYPES)