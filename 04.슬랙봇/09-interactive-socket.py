from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import logging
from pprint import pprint
import os
from dotenv import load_dotenv
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

app = App(token=SLACK_BOT_TOKEN)

@app.event("message")
def messages(event):
    pprint(event)
    text = event.get("text")
    if text == "test":
        test(event)

@app.action("action_1")
def button_click_1(ack, body, logger):
    ack()
    value = body.get("actions")[0].get("value")
    channel = body.get("channel", {}).get("id")
    app.client.chat_postMessage(channel=channel, text=f"버튼 A 클릭, value: {value}")

def test(event):
    MESSAGE_BLOCK = [{
        "type": "actions",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "버튼 A"},
                "style": "primary",
                "value": "v_1",
                "action_id": "action_1",
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "버튼 B"},
                "value": "v_2",
                "action_id": "action_2",
            }
        ]
    }]
    app.client.chat_postMessage(channel=event.get("channel"), blocks=MESSAGE_BLOCK)
if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN, logger=logger).start()