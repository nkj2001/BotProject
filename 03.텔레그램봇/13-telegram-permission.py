from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, Application, filters, MessageHandler
from dotenv import load_dotenv
import os
import logging

ADMINS = ["blographer"]

def admin_check(func):
    async def inner_function(*args, **kwargs):
        if isinstance(args[0], Update):
            update = args[0]
            if update.message.from_user.username in ADMINS:
                r = await func(*args, **kwargs)
                return r
            else:
                cmd = update.message.text
                await update.message.reply_text(text=f"해당 {cmd} 명령에 대한 권한이 없습니다.")
    return inner_function

load_dotenv()
TOKEN = os.getenv("TOKEN")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def help_command(update, context):
    await update.message.reply_text("도움말!!")

@admin_check
async def test_command(update, context):
    await update.message.reply_text("테스트!!")

application = Application.builder().token(TOKEN).build()
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("test", test_command))
application.run_polling(allowed_updates=Update.ALL_TYPES)