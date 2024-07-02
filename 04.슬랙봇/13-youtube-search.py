from slack_sdk import WebClient
from slack_bolt import App
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
from pprint import pprint
import pandas as pd
from modules import youtube
import os
import re
from dotenv import load_dotenv
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SIGNING_SECRET = os.getenv("SIGNING_SECRET")

app = App(token=SLACK_BOT_TOKEN, signing_secret=SIGNING_SECRET)
client = WebClient(SLACK_BOT_TOKEN, timeout=300)

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@app.event("message")
def handle_message(event):
    text = event.get("text")
    print(text)
    user_id = event.get("user")
    channel_id = event.get("channel")
    
def delete_all_message(event):
    r = app.client.conversations_history(channel=event.get("channel"))
    messages = r["messages"]
    for m in messages:
        client.chat_delete(channel=event.get("channel"), ts=m.get("ts"), as_user=True)

@flask_app.route("/slack/interactive", methods=["POST"])
def interactive():
    return handler.handle(request)

@flask_app.route("/slack/events", methods=["POST"])
def slack_event():
    print(f">>>>> {request} <<<<<")
    return handler.handle(request)

@flask_app.route("/slack/commands", methods=["POST"])
def commands():
    return handler.handle(request)

@app.command("/ys")
def youtube_search(ack, body, logger):
    ack()
    keyword = body.get("text")
    channel_id = body.get("channel_id")

    MESSAGE_BLOCK = [{
        "type": "actions",
        "block_id": "youtube_search",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "리스트"},
                "value": keyword,
                "action_id": "ac_yt_list",
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "엑셀"},
                "value": keyword,
                "action_id": "ac_yt_excel",
            }
        ]
    }]
    app.client.chat_postMessage(channel=channel_id, blocks=MESSAGE_BLOCK)

@app.action("ac_yt_list")
@app.action("ac_yt_excel")
def youtube_search(ack, body, logger):
    ack()
    user_id = body.get("user").get("id")
    channel_id = body.get("channel").get("id")
    keyword = body.get("actions")[0].get("value")
    action_id = body.get("actions")[0].get("action_id")
    items = youtube.search_youtube(keyword)
    BLOCKS = []
    for i, item in enumerate(items):
        if i > 20:
            break
        vid = item.get("vid")
        vtitle = item.get("vtitle")
        vcount = item.get("vcount")
        vthumb = item.get("vthumb")
        vduration = item.get("vduration")

        if action_id == "ac_yt_list":
            BLOCKS.append({"type": "divider"})
            BLOCKS.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"<https://www.youtube.com/watch?v={vid}|{vtitle}>\n조회수:{vcount}\n시간:{vduration}"},
                "accessory": {
                    "type": "image",
                    "image_url": vthumb,
                    "alt_text": "썸네일 이미지"
                }
            })
        elif action_id == "ac_yt_excel":
            BLOCKS.append([vtitle, vcount, vduration, vthumb, f"https://www.youtube.com/watch?v={vid}"])
    if action_id == "ac_yt_list":
        app.client.chat_postMessage(
            channel=channel_id,
            text=f"{keyword} 검색결과",
            blocks=BLOCKS,
            unfurl_links=False,
            unfurl_media=False
        )
    elif action_id == "ac_yt_excel":
       df = pd.DataFrame(BLOCKS, columns=["제목", "조회수", "시간", "썸네일", "링크"])
       excel_writer = pd.ExcelWriter(f"{keyword}.xlsx")
       df.to_excel(excel_writer, sheet_name=f"{keyword}", index=False)
       reg = re.compile("[가-힣]")
       for col in df:
            if reg.search(df[col].astype(str).to_string()) is None:
                col_width = max(df[col].astype(str).map(len).max(), len(col))
            else:
                col_width = max(df[col].astype(str).map(len).max() * 2, len(col))
            col_idx = df.columns.get_loc(col)
            excel_writer.sheets[keyword].set_column(col_idx, col_idx, col_width)
       excel_writer.close()
       app.client.files_upload(file=f"{keyword}.xlsx", channels=channel_id)

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8760, debug=True)