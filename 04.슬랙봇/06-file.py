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
    if text == "upimg":
        upload_image(event)
    elif text == "upmp3":
        upload_mp3(event)
    elif text == "upmp4":
        upload_mp4(event)
    elif text == "upzip":
        upload_zip(event)
    
@flask_app.route("/slack/events", methods=["POST"])
def slack_event():
    print(f">>>>> {request} <<<<<")
    return handler.handle(request)

def upload_image(event):
    result = app.client.files_upload(channels=event.get("channel"), file="python.png")
    print(result)

def upload_mp3(event):
    result = app.client.files_upload(channels=event.get("channel"), file="newdawn.mp3")
    print(result)

def upload_mp4(event):
    result = app.client.files_upload(channels=event.get("channel"), file="movie.mp4")
    print(result)

def upload_zip(event):
    result = app.client.files_upload(channels=event.get("channel"), file="chromedriver_win32.zip")
    print(result)

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8760, debug=True)