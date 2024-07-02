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
res = requests.get(url, headers=headers)
if res.status_code == 200:
    messages = res.json()
    for message in messages:
        print(message["content"])
else:
    print(f"Error {res.status_code}")