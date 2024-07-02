from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
import os
import logging

load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = 123456789
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def help_command(update, context):
    await update.message.reply_text("도움말 입니다.")

async def test(update, context):
    await context.bot.send_photo(chat_id=CHAT_ID, photo=open("python.png", "rb"))
    await update.message.reply_text("테스트 입니다.")

async def echo(update, context):
    if update.message.text.find("비디오 전송") >= 0:
        await context.bot.send_video(chat_id=CHAT_ID, video=open("movie.mp4", "rb"), write_timeout=30000)
    elif update.message.text.find("오디오 전송") >= 0:
        await context.bot.send_audio(chat_id=CHAT_ID, audio=open("newdawn.mp3", "rb"), write_timeout=30000)
    elif update.message.text.find("스티커 전송") >= 0:
        await context.bot.send_sticker(chat_id=CHAT_ID, sticker=open("python.png", "rb"))
    await update.message.reply_text(update.message.text)

application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("test", test))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
application.run_polling(allowed_updates=Update.ALL_TYPES)