from slack_sdk import WebClient
from slack_bolt import App
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
from pprint import pprint
from modules import qrcode as qrcodelib
import numpy as np
import cv2
import requests
import os
from dotenv import load_dotenv
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SIGNING_SECRET = os.getenv("SIGNING_SECRET")

app = App(token=SLACK_BOT_TOKEN, signing_secret=SIGNING_SECRET)
client = WebClient(SLACK_BOT_TOKEN, timeout=300)

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

qrcode = {}

@app.event("message")
def handle_message(event):
    text = event.get("text")
    user_id = event.get("user")
    channel_id = event.get("channel")
    q_user_id = qrcode.get(user_id)
    q_channel_id = qrcode.get(user_id, {}).get("channel_id")

    if q_user_id is not None and q_channel_id == channel_id:
        if qrcode.get(user_id).get("value") == "qr_encode":
            filepath = qrcodelib.QRCreater().make(text).png()
            app.client.files_upload(channels=channel_id, file=filepath)
            os.unlink(filepath)
        else:
            files = event.get("files", [])
            if len(files) > 0:
                if files[0].get("mimetype").find("image") >= 0:
                    url = files[0].get("url_private")
                    header = {"Authorization": f"Bearer {SLACK_BOT_TOKEN}"}
                    bytes = bytearray(requests.get(url, headers=header).content)
                    image_nparray = np.asarray(bytes, dtype=np.uint8)
                    cv_image = cv2.imdecode(image_nparray, cv2.IMREAD_COLOR)
                    results = qrcodelib.read_qrcode_zbar(cv_image)
                    output = ""
                    for r in results:
                        _data = r.get("data")
                        _type = r.get("type")
                        output += f"{_type}: {_data}\n"
                    app.client.chat_postMessage(channel=channel_id, text=output, unfurl_links=True, unfurl_media=True)
        del qrcode[user_id]

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

@app.command("/qrcode")
def com_qrcode(ack, body, logger):
    ack()
    channel_id = body.get("channel_id")
    user_id = body.get("user_id")
    user_name = body.get("user_name")
    MESSAGE_BLOCK = [{
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "인코드"},
                "value": "qr_encode",
                "action_id": "ac_qr_encode"
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "디코드"},
                "value": "qr_decode",
                "action_id": "ac_qr_decode"
            }
        ]
    }]
    app.client.chat_postMessage(channel=channel_id, blocks=MESSAGE_BLOCK)

@app.action("ac_qr_decode")
@app.action("ac_qr_encode")
def action_qrcode(ack, body, logger):
    ack()
    user_id = body.get("user").get("id")
    value = body.get("actions")[0].get("value")
    
    qrcode[user_id] = {
        "channel_id": body.get("channel").get("id"),
        "value": value
    }

    if value == "qr_encode":
        output = "QR코드로 변경될 문자열을 입력하세요."
    else:
        output = "QR코드를 분석할 이미지를 업로드 해주세요."

    response_url = body.get("response_url")
    requests.post(response_url, json={"text": output})

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8760, debug=True)