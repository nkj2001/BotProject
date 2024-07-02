import json, os

current_path = os.path.dirname(os.path.abspath(__file__))
channel_list = {}
voice_list = {}

async def save_channel_list():
    global channel_list
    with open("channels.txt", "w", encoding="utf-8") as f:
        f.write(json.dumps(channel_list))

async def load_channel_list():
    global channel_list
    if os.path.exists("channels.txt"):
        with open("channels.txt", "r", encoding="utf-8") as f:
            channel_list = json.loads(f.read())

async def save_voice_list():
    global voice_list
    with open("voice.txt", "w", encoding="utf-8") as f:
        f.write(json.dumps(voice_list))

async def load_voice_list():
    global voice_list
    if os.path.exists("voice.txt"):
        with open("voice.txt", "r", encoding="utf-8") as f:
            voice_list = json.loads(f.read())