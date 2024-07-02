from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes, InlineQueryHandler
from dotenv import load_dotenv
import os
import logging
import requests
from uuid import uuid4

load_dotenv()
TOKEN = os.getenv("TOKEN")
CHAT_ID = 123456789
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

async def inline_query(update, context):
    query = update.inline_query.query
    location = update.inline_query.location
    print(f">>>>>>>> inline: {query} Location: {location} <<<<<<<<<<<<")
    if location:
        lon = location.longitude
        lat = location.latitude
        results = get_naver_around(lon, lat)
        inlines = []
        for r in results:
            title = r.get("name")
            image = r.get("image")
            link = f"https://pcmap.place.naver.com/restaurant/{r.get('id')}/home"
            text = f'{r.get("name")}\n'
            text += f'{r.get("address")}\n'
            text += f'{r.get("tel")}\n'
            text += link
            description = r.get("description")
            inlines.append(
                InlineQueryResultArticle(
                    id = str(uuid4()),
                    title=title,
                    description=description,
                    input_message_content=InputTextMessageContent(text),
                    url=link,
                    thumbnail_url=image,
                )
            )
        await update.inline_query.answer(inlines)
    
def get_naver_around(lat, lon):
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "ko-KR,ko;q=0.8,en-US;q=0.6,en;q=0.4"
    }
    url = f"https://map.naver.com/p/api/smart-around/places?searchCoord={lat};{lon}&limit=20&sortType=RECOMMEND"
    print(f">>>>>>>>>>>>>>>> {url} <<<<<<<<<<<<<<<<<<<<<")
    logger.info(f">>>>> {url} <<<<<<<<")
    r = requests.get(url, headers=header)
    results = []
    data = r.json()
    items = data.get("result").get("list")
    for item in items:
        _rank = item.get("rank")
        _id = item.get("id")
        _name = item.get("name")
        _x = item.get("x")
        _y = item.get("y")
        _distance = item.get("distance")
        _categoryname = item.get("categoryName")
        _categorys = item.get("category")
        _category = ",".join(_categorys)
        _review_count = item.get("reviewCount")
        _address = item.get("address")
        _road_address = item.get("roadAddress")
        _tel = item.get("tel")
        images = item.get("images")
        _image = images[0] if len(images) > 0 else ""
        results.append({
            "rank": _rank,
            "id": _id,
            "name": _name,
            "x": _x,
            "y": _y,
            "distance": _distance,
            "categoryname": _categoryname,
            "category": _category,
            "review_count": _review_count,
            "address": _address,
            "road_address": _road_address,
            "tel": _tel,
            "image": _image,
            "description": item.get("description")
        })
    return results

application = Application.builder().token(TOKEN).build()
application.add_handler(InlineQueryHandler(inline_query))
application.run_polling(allowed_updates=Update.ALL_TYPES)