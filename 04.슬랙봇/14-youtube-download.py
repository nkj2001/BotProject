from slack_sdk import WebClient
from slack_bolt import App
from flask import Flask, request
from slack_bolt.adapter.flask import SlackRequestHandler
from pprint import pprint
import pandas as pd
from modules import youtube
import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import yt_dlp
import os
import re
import time
from dotenv import load_dotenv
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SIGNING_SECRET = os.getenv("SIGNING_SECRET")

app = App(token=SLACK_BOT_TOKEN, signing_secret=SIGNING_SECRET)
client = WebClient(SLACK_BOT_TOKEN, timeout=300)

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

def format_selector(ctx):
    formats = ctx.get('formats')[::-1]
    best_video = next(f for f in formats
                      if f['vcodec'] != 'none' and f['acodec'] == 'none')

    audio_ext = {'mp4': 'm4a', 'webm': 'webm'}[best_video['ext']]
    best_audio = next(f for f in formats if (
        f['acodec'] != 'none' and f['vcodec'] == 'none' and f['ext'] == audio_ext))

    yield {
        'format_id': f'{best_video["format_id"]}+{best_audio["format_id"]}',
        'ext': best_video['ext'],
        'requested_formats': [best_video, best_audio],
        'protocol': f'{best_video["protocol"]}+{best_audio["protocol"]}'
    }

@app.message(re.compile(r"https://(www\.)?(youtube|youtu)\.(com|be)/(watch\?v=|embed/)?(\S{11})"))
def message_youtube(say, context):
    channel_id = context.get("channel_id")
    respond = context.get("respond")
    user_id = context.get("user_id")
    vid = context["matches"][-1]
    url = f"https://www.youtube.com/watch?v={vid}"
    MESSAGE_BLOCK = [{
        "type": "actions",
        "block_id": "youtube",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "🎵 MP3 다운로드"},
                "value": url,
                "action_id": "ac_mp3"
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "📺 MP4 다운로드"},
                "value": url,
                "action_id": "ac_mp4"
            }
        ]
    }]
    app.client.chat_postMessage(channel=channel_id, blocks=MESSAGE_BLOCK)

@app.action("ac_mp3")
def action_download_mp3(ack, body, logger):
    ack()
    url = body.get("actions")[0].get("value")
    channel_id = body.get("channel").get("id")
    ts = body.get("message").get("ts")
    def my_hook(d):
        if d["status"] == "downloading":
            downloaded_percent = (d["downloaded_bytes"] * 100) / d["total_bytes"]
            bar = (round(downloaded_percent / 5)) * chr(9608)
            output = f"{d['filename']}\n\n{bar} {downloaded_percent:.2f} %"
            BLOCK = {
                "type": "section",
                "text": {"type": "mrkdwn", "text": output}
            }
            try:
                app.client.chat_update(channel=channel_id, ts=ts, text="update", blocks=[BLOCK])
            except:
                pass

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'nooverwrites': False,
        'progress_hooks': [my_hook],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"{url}", download=False)
        title = info.get("title", None)
        filename = re.sub('[\/:*?"<>|]', "", title)
        ydl_opts.update({"outtmpl": filename})
        yt_dlp.utils.std_headers.update({"Referer": "https://www.google.com"})
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"{url}")
            start_time = time.time()
            with open(f"{filename}.mp3", "rb") as f:
                def my_callback(monitor):
                    fsize = monitor.bytes_read
                    fpercent = (fsize * 100) / monitor.len
                    bar = (round(fpercent / 5) * chr(9608))
                    output = f"{filename}\n\n{bar} {fpercent:.2f} %"
                    BLOCK = {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": output
                        }
                    }
                    if int(fpercent) == 100 or int(time.time() - start_time) % 3 == 0:
                        app.client.chat_update(channel=channel_id, ts=ts, text="update", blocks=[BLOCK])
                e = MultipartEncoder(
                    fields={
                        "title": info.get("title"),
                        "channels": channel_id,
                        "file": (filename, f)
                    }
                )
                m = MultipartEncoderMonitor(e, my_callback)
                headers = {
                    "Content-Type": m.content_type,
                    "Authorization": f"Bearer {SLACK_BOT_TOKEN}"
                }
                try:
                    requests.post("https://slack.com/api/files.upload", data=m, headers=headers, timeout=9000)
                except Exception as e:
                    app.client.chat_postMessage(channel=channel_id, text=f"업로드 중 오류 발생!\n{e}")

            os.unlink(f"{filename}.mp3")

@app.action("ac_mp4")
def action_download_mp4(ack, body, logger):
    ack()
    url = body.get("actions")[0].get("value")
    channel_id = body.get("channel").get("id")
    ts = body.get("message").get("ts")
    def my_hook(d):
        if d["status"] == "finished":
            BLOCK = {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "다운로드 완료 후 컨버팅 시작..."
                }
            }
            app.client.chat_update(channel=channel_id, ts=ts, text="compelte", blocks=[BLOCK])
        if d["status"] == "downloading":
            downloaded_percent = (d["downloaded_bytes"] * 100) / d["total_bytes"]
            bar = (round(downloaded_percent / 5)) * chr(9608)
            output = f"{d['filename']}\n\n{bar} {downloaded_percent:.2f} %"
            BLOCK = {
                "type": "section",
                "text": {"type": "mrkdwn", "text": output}
            }
            try:
                app.client.chat_update(channel=channel_id, ts=ts, text="update", blocks=[BLOCK])
            except:
                pass

    ydl_opts = {
        'format': format_selector,
        'nooverwrites': False,
        'progress_hooks': [my_hook],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"{url}", download=False)
        title = info.get("title", None)
        filename = ydl.prepare_filename(info)
        ydl_opts.update({"outtmpl": filename})
        yt_dlp.utils.std_headers.update({"Referer": "https://www.google.com"})
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"{url}")
            start_time = time.time()
            with open(f"{filename}", "rb") as f:
                def my_callback(monitor):
                    fsize = monitor.bytes_read
                    fpercent = (fsize * 100) / monitor.len
                    bar = (round(fpercent / 5) * chr(9608))
                    output = f"{filename}\n\n{bar} {fpercent:.2f} %"
                    BLOCK = {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": output
                        }
                    }
                    if int(fpercent) == 100 or int(time.time() - start_time) % 3 == 0:
                        app.client.chat_update(channel=channel_id, ts=ts, text="update", blocks=[BLOCK])
                e = MultipartEncoder(
                    fields={
                        "title": info.get("title"),
                        "channels": channel_id,
                        "file": (filename, f)
                    }
                )
                m = MultipartEncoderMonitor(e, my_callback)
                headers = {
                    "Content-Type": m.content_type,
                    "Authorization": f"Bearer {SLACK_BOT_TOKEN}"
                }
                try:
                    requests.post("https://slack.com/api/files.upload", data=m, headers=headers, timeout=9000)
                except Exception as e:
                    app.client.chat_postMessage(channel=channel_id, text=f"업로드 중 오류 발생!\n{e}")

            os.unlink(f"{filename}")

@flask_app.route("/slack/interactive", methods=["POST"])
def interactive():
    return handler.handle(request)

@flask_app.route("/slack/events", methods=["POST"])
def slack_event():
    print(f">>>>> {request} <<<<<")
    return handler.handle(request)

@flask_app.route("/slack/commands", methods=["POST"])
def commands():
    return handler.handle(request)

@app.command("/ys")
def youtube_search(ack, body, logger):
    ack()
    keyword = body.get("text")
    channel_id = body.get("channel_id")

    MESSAGE_BLOCK = [{
        "type": "actions",
        "block_id": "youtube_search",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "리스트"},
                "value": keyword,
                "action_id": "ac_yt_list",
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "엑셀"},
                "value": keyword,
                "action_id": "ac_yt_excel",
            }
        ]
    }]
    app.client.chat_postMessage(channel=channel_id, blocks=MESSAGE_BLOCK)

@app.action("ac_yt_list")
@app.action("ac_yt_excel")
def youtube_search(ack, body, logger):
    ack()
    user_id = body.get("user").get("id")
    channel_id = body.get("channel").get("id")
    keyword = body.get("actions")[0].get("value")
    action_id = body.get("actions")[0].get("action_id")
    items = youtube.search_youtube(keyword)
    BLOCKS = []
    for i, item in enumerate(items):
        if i > 10:
            break
        vid = item.get("vid")
        vtitle = item.get("vtitle")
        vcount = item.get("vcount")
        vthumb = item.get("vthumb")
        vduration = item.get("vduration")

        if action_id == "ac_yt_list":
            BLOCKS.append({"type": "divider"})
            BLOCKS.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"<https://www.youtube.com/watch?v={vid}|{vtitle}>\n조회수:{vcount}\n시간:{vduration}"},
                "accessory": {
                    "type": "image",
                    "image_url": vthumb,
                    "alt_text": "썸네일 이미지"
                }
            })
            BLOCKS.append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "🎵 MP3 다운로드"
                        },
                        "value": f"https://www.youtube.com/watch?v={vid}",
                        "action_id": "ac_mp3"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "emoji": True,
                            "text": "📻 MP4 다운로드"
                        },
                        "value": f"https://www.youtube.com/watch?v={vid}",
                        "action_id": "ac_mp4"
                    }
                ]
            })
        elif action_id == "ac_yt_excel":
            BLOCKS.append([vtitle, vcount, vduration, vthumb, f"https://www.youtube.com/watch?v={vid}"])
    if action_id == "ac_yt_list":
        app.client.chat_postMessage(
            channel=channel_id,
            text=f"{keyword} 검색결과",
            blocks=BLOCKS,
            unfurl_links=False,
            unfurl_media=False
        )
    elif action_id == "ac_yt_excel":
       df = pd.DataFrame(BLOCKS, columns=["제목", "조회수", "시간", "썸네일", "링크"])
       excel_writer = pd.ExcelWriter(f"{keyword}.xlsx")
       df.to_excel(excel_writer, sheet_name=f"{keyword}", index=False)
       reg = re.compile("[가-힣]")
       for col in df:
            if reg.search(df[col].astype(str).to_string()) is None:
                col_width = max(df[col].astype(str).map(len).max(), len(col))
            else:
                col_width = max(df[col].astype(str).map(len).max() * 2, len(col))
            col_idx = df.columns.get_loc(col)
            excel_writer.sheets[keyword].set_column(col_idx, col_idx, col_width)
       excel_writer.close()
       app.client.files_upload(file=f"{keyword}.xlsx", channels=channel_id)

if __name__ == "__main__":
    flask_app.run(host="0.0.0.0", port=8760, debug=True)