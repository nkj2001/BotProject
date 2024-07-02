import os
from dotenv import load_dotenv
import requests
import time

load_dotenv()
TOKEN = os.getenv("TOKEN")

old_id = 0
try:
    with open("__save_id", "r") as f:
        old_id = int(f.read().strip())
except:
    pass

while True:
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates?offset={old_id}"
    r = requests.get(url)
    data = r.json()
    for item in data.get("result"):
        print(item)
        new_id = item.get("update_id")
        if old_id < new_id:
            old_id = new_id
            with open("__save_id", "w") as f:
                f.write(str(old_id))
        message = item["message"].get("text")
        print(message)
    time.sleep(1)