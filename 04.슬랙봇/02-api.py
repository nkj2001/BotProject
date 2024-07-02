import requests
import os
from dotenv import load_dotenv
load_dotenv()
SLACK_TOKEN = os.getenv("TOKEN")

CHANNEL_ID = "----------"
headers = {"Authorization": f"Bearer {SLACK_TOKEN}"}

def send_message():
    url = "https://slack.com/api/chat.postMessage"
    data = {
        "Content-Type": "application/x-www-form-urlencoded",
        "channel": CHANNEL_ID,
        "text": "안녕 슬랙 봇!!!"
    }

    res = requests.post(url, data=data, headers=headers)
    print(res.text)

def get_message():
    url = f"https://slack.com/api/conversations.history?channel={CHANNEL_ID}"
    res = requests.get(url, headers=headers)
    print(res.text)

url = "https://slack.com/api/chat.delete"
data = {
    "Content-Type": "application/x-www-form-urlencoded",
    "channel": CHANNEL_ID,
    "ts": "1712262186.696169"
}

res = requests.post(url, data=data, headers=headers)
print(res.text)