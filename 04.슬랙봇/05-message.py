from slack_sdk import WebClient
from slack_bolt import App
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
from pprint import pprint
import os
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
    pprint(event)
    text = event.get("text")
    if text == "test":
        send_test(event)
    elif text == "image":
        send_image(event)
    elif text == "mul":
        send_multiple(event)
    #app.client.chat_postMessage(channel=event.get("channel"), as_user=True, text=event.get("text"))

@app.event("reaction_added")
def reaction(event):
    pprint(event)

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

def send_image(event):
    message_block = {
        "channel": event.get("channel"),
        "text": "test",
        "blocks": [
            {
                "type": "image",
                "title": {
                    "type": "plain_text",
                    "text": "I love tacos",
                    "emoji": True
                },
                "image_url": "https://assets3.thrillist.com/v1/image/1682388/size/tl-horizontal_main.jpg",
                "alt_text": "delicious tacos"
            }
        ]
    }
    app.client.chat_postMessage(**message_block)

def send_multiple(event):
    message_block = {
        "channel": event.get("channel"),
        "text": "",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "다양한 형태의 메세지 블록입니다."
                }
            },
            {
                "type": "divider"
            }
        ]
    }

    for i in range(3):
        message_block.get("blocks").append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{i}번째 항목*\n다음줄 텍스트\n평점: 9.4"
            },
            "accessory": {
                "type": "image",
                "image_url": "https://api.slack.com/img/blocks/bkb_template_images/tripAgent_1.png",
                "alt_text": "이미지 설명"
            }
        })
        message_block.get("blocks").append({
            "type": "context",
            "elements": [
                {
                    "type": "image",
                    "image_url": "https://api.slack.com/img/blocks/bkb_template_images/tripAgentLocationMarkder.png",
                    "alt_text": "위치 아이콘"
                },
                {
                    "type": "plain_text",
                    "emoji": True,
                    "text": "위치: 대한민국 서울"
                }
            ]
        })
        message_block.get("blocks").append({"type": "divider"})
    app.client.chat_postMessage(**message_block)

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8760, debug=True)