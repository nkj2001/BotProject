from slack_sdk import WebClient
from slack_bolt import App
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
from pprint import pprint
from modules import money_exchange_rate as mer
from modules import weather
import requests
import os
import json
import re
from dotenv import load_dotenv
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_USER_TOKEN = os.getenv("SLACK_USER_TOKEN")
SIGNING_SECRET = os.getenv("SIGNING_SECRET")

app = App(token=SLACK_BOT_TOKEN, signing_secret=SIGNING_SECRET)
client = WebClient(SLACK_USER_TOKEN, timeout=300)

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

CURRENCY_LIST = ["달러", "위안", "엔", "유로", "페소", "루블", "홍콩달러", "호주달러"]

@app.message(re.compile(f"^([0-9]+\s?)({"|".join(CURRENCY_LIST)})+$"))
def money_exchange_to(say, context):
    v = context['matches'][0]
    k = context['matches'][1]
    money, source, target = mer.google_money_exchange_rate(f"{v} {k}")
    output = f"{v}{k} ==> {money} {target}"
    say(text=output)

@app.message(re.compile("^[0-9]+\s?원$"))
def money_exchange(say, context):
    r = context['matches'][0]
    MESSAGE_BLOCK = [
        {
            "type": "actions",
            "block_id": "exchange",
            "elements": []
        }
    ]
    for c in CURRENCY_LIST:
        MESSAGE_BLOCK[0].get("elements").append({
            "type": "button",
            "text": {"type": "plain_text", "text": c},
            "value": f"{r}^{c}",
            "action_id": f"exchange_{c}"
        })
    say(blocks=MESSAGE_BLOCK, text="_")

@flask_app.route("/slack/interactive", methods=["POST"])
def slack_interactive():
    data = json.loads(request.form["payload"])
    response = data.get("message")
    channel = data.get("channel").get("id")
    user = data.get("user").get("id")
    if data.get("type") == "block_actions":
        block_id = data.get("actions")[0].get("block_id")
        value = data.get("actions")[0].get("value")
        if block_id == "exchange":
            v, k = value.split("^")
            money, source, target = mer.google_money_exchange_rate(v, to=k)
            output = f"{money} {target}"
            output += f" {v} ==> {money} {target}"
            requests.post(data["response_url"], json={"text": output})
    return ''

@flask_app.route("/slack/events", methods=["POST"])
def slack_event():
    print(f">>>>> {request} <<<<<")
    return handler.handle(request)

def delete_all_message(event):
    r = app.client.conversations_history(channel=event.get("channel"))
    messages = r["messages"]
    for m in messages:
        client.chat_delete(channel=event.get("channel"), ts=m.get("ts"), as_user=True)

@app.message(re.compile("^([가-힣]{2})\s?날씨$"))
def get_weather(say, context):
    v = context['matches'][0]
    w = weather.get_weather(v)
    output = ""
    for k, v in w.items():
        output += f"{k}: {v}\n"
    say(text=output)

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8760, debug=True)