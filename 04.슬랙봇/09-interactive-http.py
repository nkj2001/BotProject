from slack_sdk import WebClient
from slack_bolt import App
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
from pprint import pprint
import json
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
    if text == "test2":
        test2(event)

@flask_app.route("/slack/events", methods=["POST"])
def slack_event():
    print(f">>>>> {request} <<<<<")
    return handler.handle(request)

@flask_app.route("/slack/interactive", methods=["POST"])
def interactive():
    return handler.handle(request)

@app.action("action_1")
def action_1(ack, body, logger):
    ack()
    print("ACTION1")

def test2(event):
    MESSAGE_BLOCK = {
        "type": "section",
        "text": {
            "type": "plain_text",
            "text": "This is a plain text section block.",
            "emoji": True
        },
        "accessory": {
            "type": "static_select",
            "placeholder": {
                "type": "plain_text",
                "text": "Select an item",
                "emoji": True
            },
            "options": [
                {
                    "text": {
                        "type": "plain_text",
                        "text": "*plain_text option 0*",
                        "emoji": True
                    },
                    "value": "value-0"
                },
                {
                    "text": {
                        "type": "plain_text",
                        "text": "*plain_text option 2*",
                        "emoji": True
                    },
                    "value": "value-2"
                }
            ],
            "action_id": "static_select-action"
        }
    }
    app.client.chat_postMessage(channel=event.get("channel"), blocks=[MESSAGE_BLOCK])

@app.action("static_select-action")
def action_static(ack, body, logger):
    ack()
    value = body.get("actions")[0].get("selected_option").get("value")
    print(value)
if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8760, debug=True)