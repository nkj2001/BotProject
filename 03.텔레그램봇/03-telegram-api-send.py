import os
from dotenv import load_dotenv
import requests
import time
import json

load_dotenv()
TOKEN = os.getenv("TOKEN")

header = {"Content-Type": "application/json"}

def sendMessage(chat_id, message, protect=False, disable_notification=False, parse_mode=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message
    }

    if protect:
        data.update({"protect_content": True})
    if disable_notification:
        data.update({"disable_notification": True})
    if parse_mode is not None:
        data.update({"parse_mode": parse_mode})
    data = json.dumps(data)
    r = requests.post(url, headers=header, data=data)
    return r.json()

def sendPhoto(chat_id, file, caption=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendPhoto"
    params = {"chat_id": chat_id}
    files = {"photo": file}
    if caption is not None:
        params.update({"caption": caption})
    r = requests.post(url, data=params, files=files)
    return r.json()

def sendVideo(chat_id, file, caption=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
    params = {"chat_id": chat_id}
    files = {"video": file}
    if caption is not None:
        params.update({"caption": caption})
    r = requests.post(url, data=params, files=files)
    return r.json()

def sendAudio(chat_id, file, caption=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendAudio"
    params = {"chat_id": chat_id}
    files = {"audio": file}
    if caption is not None:
        params.update({"caption": caption})
    r = requests.post(url, data=params, files=files)
    return r.json()

def sendDocument(chat_id, file, caption=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
    params = {"chat_id": chat_id}
    files = {"document": file}
    if caption is not None:
        params.update({"caption": caption})
    r = requests.post(url, data=params, files=files)
    return r.json()

def sendChatAction(chat_id, action):
    url = f"https://api.telegram.org/bot{TOKEN}/sendChatAction"
    params = {
        "chat_id": chat_id,
        "action": action
    }
    r = requests.post(url, data=params)
    return r.json()

def sendVenue(chat_id, lat, lon, title, address):
    url = f"https://api.telegram.org/bot{TOKEN}/sendVenue"
    params = {
        "chat_id": chat_id,
        "latitude": lat,
        "longitude": lon,
        "title": title,
        "address": address
    }
    r = requests.post(url, data=params)
    return r.json()

def sendContact(chat_id, phone, first_name, vcard=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendContact"
    params = {
        "chat_id": chat_id,
        "phone_number": phone,
        "first_name": first_name
    }
    if vcard is not None:
        params.update({"vcard": vcard})
    r = requests.post(url, data=params)
    return r.json()

# message_html = """
# 안녕 난 <b>텔레그램 봇</b>입니다.
# <i>이태릭 글자도 전송 가능</i>
# <code>import requests</code>
# <u>언더라인</u><s>스트라이크</s>
# """
# print(sendMessage(7198424709, message_html, protect=True, disable_notification=True, parse_mode="HTML"))
#print(sendPhoto(7198424709, open("python.png", "rb"), "파이썬 로고"))
#print(sendVideo(7198424709, open("movie.mp4", "rb"), "파이썬 로고"))
#print(sendAudio(7198424709, open("newdawn.mp3", "rb"), "샘플오디오"))
#print(sendDocument(7198424709, open("chromedriver_win32.zip", "rb"), "샘플오디오"))
#print(sendChatAction(7198424709, "upload_video"))
#print(sendVenue(7198424709, 37.6829715, 127.0904238, "테스트", "주소123"))

data = "BEGIN:VCARD\n"
data += "VERSION:3.0\n"
data += "FN:남박사\n"
data += "TEL;TYPE=WORK;CELL:010 1234 1234\n"
data += "EMAIL;TYPE=WORK:abcd@gmail.com\n"
data += "URL;TYPE=WORK:https://www.naver.com\n"
data += "END:VCARD\n"
print(sendContact(7198424709, "010-1234-1234", "남박사", data))

