from telegram import Update
from telegram.ext import CommandHandler, CallbackContext, Application, filters, MessageHandler, BaseHandler
from dotenv import load_dotenv
import os
import logging

ADMINS = ["blographer"]
CMDS = ["/test"]

class AdminHandler(BaseHandler):
    def __init__(self):
        super().__init__(self.block)

    async def block(self, update, context):
        await update.message.reply_text(f"{update.message.text} 명령어를 처리할 권한이 없습니다.")
    
    def check_update(self, update):
        if update.message is not None:
            if update.message.text in CMDS and update.message.from_user.username not in ADMINS:
                return True
        return False

load_dotenv()
TOKEN = os.getenv("TOKEN")
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def help_command(update, context):
    await update.message.reply_text("도움말!!")

async def test_command(update, context):
    await update.message.reply_text("테스트!!")

application = Application.builder().token(TOKEN).build()
application.add_handler(AdminHandler())
application.add_handler(CommandHandler("help", help_command))
application.add_handler(CommandHandler("test", test_command))
application.run_polling(allowed_updates=Update.ALL_TYPES)