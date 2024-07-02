from flask import Flask, request, jsonify
from pprint import pprint
from youtube_transcript_api import YouTubeTranscriptApi
import re

app = Flask(__name__)

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

@app.route("/fallback", methods=["POST"])
def fallback_skill():
    content = request.get_json()
    output = "죄송합니다. 알아듣지 못했습니다."
    pprint(content)
    user_request = content.get("userRequest")
    if user_request:
        utterance = user_request.get("utterance")
        vid = is_youtube_url(utterance)
        if vid is not None:
            transcript = get_transcript(vid, languages=['ko'])
            if transcript is not None:
                output = ""
                for t in transcript:
                    output += f"{t.get('text')}"

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