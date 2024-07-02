from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler, InlineQueryHandler, Application
import yt_dlp
from uuid import uuid4
from modules import youtube
import re
import logging
import os
import asyncio
from dotenv import load_dotenv
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("TOKEN")

async def start_youtube(update, context):
    keyboard = [
        [
            InlineKeyboardButton("MP3 다운", callback_data="mp3"),
            InlineKeyboardButton("취소", callback_data="nothing"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.user_data["url"] = update.message.text
    await update.message.reply_text("어떤 처리를 할까요?", reply_markup=reply_markup)

async def send_async_message(context, chat_id, text):
    await context.bot.send_message(chat_id=chat_id, text=text)

async def edit_async_message(saved, text):
    await saved.edit_text(text)

async def inline_youtube_handler(update, context):
    query = update.callback_query
    data = query.data
    if data == "nothing":
        await query.delete_message()
        return
    url = context.user_data["url"]
    saved = await query.edit_message_text("분석중...")

    def my_hook(d):
        if d['status'] == "finished":
            loop = asyncio.get_event_loop()
            #loop.create_task(send_async_message(context, chat_id=query.message.chat_id, text="변환중..."))
            loop.create_task(edit_async_message(saved, "변환중..."))
        if d['status'] == "downloading":
            downloaded_percent = (d["downloaded_bytes"] *100) / d["total_bytes"]
            print(downloaded_percent)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'nooverwrites': False,
        'logger': MyLogger(),
        'progress_hooks': [my_hook],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"{url}", download=False)
        title = info.get("title", None)
        duration = info.get("duration", 0)
    if duration / 60 / 60 > 40:
        delete = await context.bot.send_message(chat_id=query.message.chat_id, text="동영상이 너무 깁니다.")
    else:
        filename = re.sub(r'[\/:*?"]"<>|]', '', title)
        ydl_opts.update({"outtmpl": filename})
        yt_dlp.utils.std_headers.update({"Referer": "https://www.google.com"})
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"{url}")
            #delete = await context.bot.send_message(chat_id=query.message.chat_id, text="업로드 중....")
            await saved.edit_text("업로드 중..")
            await context.bot.send_audio(chat_id=query.message.chat_id, audio=open(f"{filename}.mp3", "rb"), write_timeout=600000)
            #await delete.delete()
            os.unlink(f"{filename}.mp3")

class MyLogger():
    def debug(self, msg):
        if msg.startswith('[debug]'):
            pass
        else:
            self.info(msg)
    def info(self, msg):
        pass
    def warning(self, msg):
        pass
    def error(self, msg):
        print(msg)

async def inlinequery(update, context):
    query = update.inline_query.query
    if len(query) > 2:
        inlines = []
        results = youtube.search_youtube(query)
        for r in results:
            vid = r.get("vid")
            title = r.get("vtitle")
            count = r.get("vcount")
            thumb = r.get("vthumb")
            duration = r.get("vduration")
            url = f"https://www.youtube.com/watch?v={vid}"
            text = f"{duration} / {count}\n"
            inlines.append(
                InlineQueryResultArticle(
                    id=str(uuid4()),
                    title=title,
                    description=text,
                    input_message_content=InputTextMessageContent(url),
                    url=url,
                    thumbnail_url=thumb
                )
            )
        await update.inline_query.answer(inlines)

filter_youtube = filters.Regex(r"^https:\/\/(www\.)?(youtube.com|youtube.be)\/(watch|embed)?(v=|\/)?(\S+)$")
application = Application.builder().token(TOKEN).build()
application.add_handler(MessageHandler(filter_youtube, start_youtube))
application.add_handler(CallbackQueryHandler(inline_youtube_handler))
application.add_handler(InlineQueryHandler(inlinequery))
application.run_polling(allowed_updates=Update.ALL_TYPES)