from flask import Flask, request, jsonify
from pprint import pprint
from youtube_transcript_api import YouTubeTranscriptApi
import re
from kiwipiepy import Kiwi
from dotenv import load_dotenv
import os
from openai import OpenAI
import requests
import threading

load_dotenv()
OPENAI_KEY = os.getenv("OPENAI_KEY")

client = OpenAI(api_key=OPENAI_KEY)
app = Flask(__name__)

@app.route("/image_descript", methods=["POST"])
def image_descript():
    content = request.get_json()
    pprint(content)
    user_request = content.get("userRequest")
    callback_url = user_request.get("callbackUrl")
    context = content.get("contexts")
    image_url = None
    for c in context:
        if c.get("name") == "ImageContext":
            image_url = c.get("params").get("ImageURL").get("value")
            break
    if image_url is not None:
        threading.Thread(target=image_process, args=(image_url, callback_url, 1)).start()
    return jsonify({
        "version": "2.0",
        "useCallback": True,
        "data": {
            "text": "처리 중입니다. 잠시 기다려 주세요.."
        }
    })

@app.route("/image_ocr", methods=["POST"])
def image_ocr():
    content = request.get_json()
    pprint(content)
    user_request = content.get("userRequest")
    callback_url = user_request.get("callbackUrl")
    context = content.get("contexts")
    image_url = None
    for c in context:
        if c.get("name") == "ImageContext":
            image_url = c.get("params").get("ImageURL").get("value")
            break
    if image_url is not None:
        threading.Thread(target=image_process, args=(image_url, callback_url, 2)).start()
    return jsonify({
        "version": "2.0",
        "useCallback": True,
        "data": {
            "text": "처리 중입니다. 잠시 기다려 주세요.."
        }
    })

def contains_image_url(text):
    pattern = r"https://talk\.kakaocdn\.net/[\w/.\-?=&%]+\.jpg"
    if re.search(pattern, text):
        return True
    else:
        return False

def image_process(image_url, callback_url, mode=1):
    if mode == 1:
        output = "이미지에 대해서 자세히 설명해줘."
    else:
        output = "이미지에서 보이는 모든 글자를 추출해줘"

    response = client.chat.completions.create(
        model="gpt-4-turbo-2024-04-09",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": output},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url
                        }
                    }
                ]
            }
        ]
    )
    requests.post(callback_url, json={
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": response.choices[0].message.content
                    }
                }
            ]
        }
    })
def get_chat_complete(prompt):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

def is_youtube_url(text):
    pattern = r"(https?://)?(www\.)?youtube\.com/watch\?v=([\w-]+)(&\S*)?|youtu\.be/([\w-]+)"
    match = re.match(pattern, text)
    if match:
        return match.group(3) or match.group(5)
    else:
        return None

def get_transcript(video_id, languages=["en"]):
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    transcript = transcript_list.find_transcript(languages)
    return transcript.fetch()

def get_youtube_transcript(vid, callback_url):
    transcript = get_transcript(vid, languages=['ko'])
    if transcript is not None:
        output = ""
        for t in transcript:
            output += f"{t.get('text')}"
        kiwi = Kiwi()
        sents = kiwi.split_into_sents(output)
        output = "\n".join([s.text for s in sents])
        prompt = f'"""{output}"""\n\n위의 내용을 300자 내외로 요약해주세요.'
        summary = get_chat_complete(prompt)
        output = summary
        c = requests.post(callback_url, json={
            "version": "2.0",
            "template": {
                "outputs": [
                    {
                        "simpleText": {
                            "text": output
                        }
                    }
                ]
            }
        })
        print(c.status_code, c.json())

@app.route("/fallback", methods=["POST"])
def fallback_skill():
    content = request.get_json()
    output = "죄송합니다. 알아듣지 못했습니다."
    pprint(content)
    user_request = content.get("userRequest")
    callback_url = user_request.get("callbackUrl")
    if user_request:
        utterance = user_request.get("utterance")
        vid = is_youtube_url(utterance)
        if vid is not None:
            threading.Thread(target=get_youtube_transcript, args=(vid, callback_url)).start()
            return jsonify({
                "version": "2.0",
                "useCallback": True,
                "data": {
                    "text": "처리 중입니다. 잠시 기다려 주세요.."
                }
            })
        elif contains_image_url(utterance):
            result_json = {
                "version": "2.0",
                "template": {
                    "outputs": [
                        {
                            "simpleText": {
                                "text": "어떤 기능을 처리할까요?"
                            }
                        }
                    ],
                    "quickReplies": [
                        {
                            "action": "block",
                            "blockId": "662970017e38b9231002fc71",
                            "label": "이미지 분석"
                        },
                        {
                            "action": "block",
                            "blockId": "6629700c341f2657b904c7d5",
                            "label": "이미지 OCR"
                        }
                    ]
                },
                "context": {
                    "values": [
                        {
                            "name": "ImageContext",
                            "lifeSpan": 5,
                            "ttl": 600,
                            "params": {
                                "ImageURL": utterance
                            }
                        }
                    ]
                }
            }
            return jsonify(result_json)
            threading.Thread(target=descript_image, args=(utterance, callback_url)).start()
            return jsonify({
                "version": "2.0",
                "useCallback": True,
                "data": {
                    "text": "처리 중입니다. 잠시 기다려 주세요.."
                }
            })

    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": output
                    }
                }
            ]
        }
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8763)