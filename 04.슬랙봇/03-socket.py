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

@app.event("reaction_added")
def reaction(event):
    pprint(event)

if __name__ == "__main__":
    SocketModeHandler(app, SLACK_APP_TOKEN, logger=logger).start()