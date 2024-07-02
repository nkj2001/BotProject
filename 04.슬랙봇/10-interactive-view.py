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

@app.action("action_9")
def action9(ack, body, logger):
    ack()
    app.client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "view_opinion",
            "title": {"type": "plain_text", "text": "의견"},
            "submit": {"type": "plain_text", "text": "전송"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "input_c",
                    "label": {"type": "plain_text", "text": "의견을 작성해주세요."},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "opinion_input",
                        "multiline": True
                    }
                }
            ]
        }
    )

@app.action("action_bug")
def action9(ack, body, logger):
    ack()
    app.client.views_open(
        trigger_id=body["trigger_id"],
        view={
            "type": "modal",
            "callback_id": "view_bug",
            "title": {"type": "plain_text", "text": "버그리포트"},
            "submit": {"type": "plain_text", "text": "전송"},
            "blocks": [
                {
                    "type": "input",
                    "block_id": "input_title",
                    "label": {"type": "plain_text", "text": "제목"},
                    "element": {
                        "type": "plain_text_input",
                        "action_id": "bug_title",
                    }
                },
                {
                    "type": "input",
                    "block_id": "input_contents",
                    "label": {"type": "plain_text", "text": "내용"},
                    "element": {
                        "type": "plain_text_input",
                        "multiline": True,
                        "action_id": "bug_contents",
                    }
                },
                {
                    "type": "input",
                    "block_id": "input_options",
                    "label": {"type": "plain_text", "text": "버그유형"},
                    "element": {
                        "type": "static_select",
                        "placeholder": {"type": "plain_text", "text": "버그종류를 선택하세요."},
                        "action_id": "bug_options",
                        "options": [
                            {"text": {"type": "plain_text", "text": "일반버그"}, "value": "bug_option_1"},
                            {"text": {"type": "plain_text", "text": "그냥버그"}, "value": "bug_option_2"},
                            {"text": {"type": "plain_text", "text": "심각버그"}, "value": "bug_option_3"},
                        ]
                    }
                }
            ]
        }
    )

@app.view("view_bug")
def view_bug_report(ack, body, client, view, logger):
    ack()
    b_title = view.get("state").get("values").get("input_title").get("bug_title").get("value")
    b_contents = view.get("state").get("values").get("input_contents").get("bug_contents").get("value")
    b_options = view.get("state").get("values").get("input_options").get("bug_options").get("selected_option").get("value")
    print(f"title:{b_title}")
    print(f"contents:{b_contents}")
    print(f"options:{b_options}")

@app.view("view_opinion")
def view_my_opinion(ack, body, client, view, logger):
    ack()
    value = view.get("state").get("values").get("input_c").get("opinion_input").get("value")
    user = body.get("user").get("id")
    print(f"user: {user}")
    print(f"value: {value}")

@app.event("message")
def handle_message(event):
    pprint(event)
    text = event.get("text")
    if text == "view":
        MESSAGE_BLOCK = [{
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "뷰시작"},
                    "value": "v_9",
                    "action_id": "action_9"
                }
            ]
        }]
        app.client.chat_postMessage(channel=event.get("channel"), blocks=MESSAGE_BLOCK)
    elif text == "bug":
        MESSAGE_BLOCK = [{
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "버그리포트"},
                    "value": "v_9",
                    "action_id": "action_bug"
                }
            ]
        }]
        app.client.chat_postMessage(channel=event.get("channel"), blocks=MESSAGE_BLOCK)

@flask_app.route("/slack/events", methods=["POST"])
def slack_event():
    return handler.handle(request)

@flask_app.route("/slack/interactive", methods=["POST"])
def interactive():
    return handler.handle(request)

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8760, debug=True)