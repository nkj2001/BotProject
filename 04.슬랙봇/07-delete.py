from slack_sdk import WebClient
from slack_bolt import App
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
from pprint import pprint
import os
from dotenv import load_dotenv
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_USER_TOKEN = os.getenv("SLACK_USER_TOKEN")
SIGNING_SECRET = os.getenv("SIGNING_SECRET")

app = App(token=SLACK_BOT_TOKEN, signing_secret=SIGNING_SECRET)
client = WebClient(SLACK_USER_TOKEN, timeout=300)

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@app.event("message")
def handle_message(event):
    pprint(event)
    text = event.get("text")
    if text == "test":
        send_test(event)
    elif text == "delete":
        delete_all_message(event)
    
@flask_app.route("/slack/events", methods=["POST"])
def slack_event():
    print(f">>>>> {request} <<<<<")
    return handler.handle(request)

def send_test(event):
    message_block = {
        "channel": event.get("channel"),
        "text": "aaaa",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "버튼이 포함된 텍스트 입니다.\n*마크다운* 문법을 지원합니다.\n`코드표현식`"
                },
                "accessory": {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "구글링크🧡",
                        "emoji": True
                    },
                    "value": "click_me_123",
                    "url": "https://www.google.com",
                    "action_id": "button-action"
                }
            }
        ]
    }
    app.client.chat_postMessage(**message_block)

def delete_all_message(event):
    r = app.client.conversations_history(channel=event.get("channel"))
    messages = r["messages"]
    for m in messages:
        client.chat_delete(channel=event.get("channel"), ts=m.get("ts"), as_user=True)

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8760, debug=True)