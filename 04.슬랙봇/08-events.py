from slack_sdk import WebClient
from slack_bolt import App
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
from pprint import pprint
import os
import notice
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
    
@flask_app.route("/slack/events", methods=["POST"])
def slack_event():
    print(f">>>>> {request} <<<<<")
    return handler.handle(request)

notice_history = {}
@app.event("member_joined_channel")
def member_join_channel(event):
    channel = event.get("channel")
    user_id = event.get("user")
    _notice = notice.Notice(channel, user_id, app)
    message = _notice.get_message()
    res = app.client.chat_postMessage(**message)
    _notice.timestamp = res.get("ts")
    if f"@{user_id}" not in notice_history:
        notice_history[f"@{user_id}"] = {}
    notice_history[f"@{user_id}"][user_id] = _notice

@app.event("reaction_added")
def reaction(event):
    channel = event.get("item", {}).get("channel")
    ts = event.get("item", {}).get("ts")
    user = event.get("user")
    if f"@{user}" not in notice_history:
        return
    _notice = notice_history[f"@{user}"][user]
    if _notice.timestamp == ts:
        _notice.read = True
        _notice.channel = channel
        message = _notice.get_message()
        updated_message = app.client.chat_update(**message)
        _notice.timestamp = updated_message.get("ts")

@app.event("member_left_channel")
def member_left_channel(event):
    pprint(event)

@app.event("team_join")
def team_join(event):
    pprint(event)

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8760, debug=True)