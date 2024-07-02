from dotenv import load_dotenv
import os
import requests
load_dotenv()
TOKEN = os.getenv("TOKEN")
CHANNEL_ID = "1233161237261717586"

url = f"https://discord.com/api/v10/channels/{CHANNEL_ID}/messages"
headers = {
    "Authorization": f"Bot {TOKEN}"
}

data = {
    "content": "디스코드 봇이 메세지를 전송합니다."
}

res = requests.post(url, headers=headers, json=data)
if res.status_code == 200:
    r = res.json()
    print(r)
else:
    print(f"Error {res.status_code}")