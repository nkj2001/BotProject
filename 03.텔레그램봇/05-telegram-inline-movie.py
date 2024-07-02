from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, InlineQueryHandler
from dotenv import load_dotenv
from modules.movie import search_movie_daum
import os
import logging
import re
from uuid import uuid4

load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = 123456789
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def inline_query(update, context):
    query = update.inline_query.query
    if query == "":
        return
    print(f">>>>>>>> inline: {query} <<<<<<<<<<<<")
    results = search_movie_daum(query)
    title = results.get("title")
    url = results.get("thumbnail")
    text = ""
    for k, v in results.get("info").items():
        text += f"{k}: {v}\n"
    await update.inline_query.answer([InlineQueryResultArticle(id=str(uuid4()), 
                                                               title=title, 
                                                               thumbnail_url=url, 
                                                               description=text, 
                                                               input_message_content=InputTextMessageContent(text))])

application = Application.builder().token(TOKEN).build()
application.add_handler(InlineQueryHandler(inline_query))
application.run_polling(allowed_updates=Update.ALL_TYPES)