import requests
import json

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}

def find_key(data, target_key):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == target_key:
                yield value
            else:
                yield from find_key(value, target_key)
    elif isinstance(data, list):
        for item in data:
            yield from find_key(item, target_key)

def search_youtube(keyword):
    results = []
    url = f"https://www.youtube.com/results?search_query={keyword}"
    r = requests.get(url, headers=header)
    p_start = "var ytInitialData = "
    p_end = "};"

    index_start = r.text.find(p_start)
    index_end = r.text.find(p_end, index_start)
    
    if index_end < index_start:
        return results
    
    data = r.text[index_start + len(p_start) : index_end + 1]
    _json = json.loads(data)
    contents = _json.get("contents").get("twoColumnSearchResultsRenderer").get("primaryContents").get("sectionListRenderer").get("contents")
    video_renderer = list(find_key(contents, "videoRenderer"))

    for vr in video_renderer:
        vid = vr.get("videoId")
        vthumb = vr.get("thumbnail").get("thumbnails")[0].get("url")
        vlength = vr.get("lengthText")
        if vlength is None:
            continue
        vduration = vlength.get("simpleText")
        vcount = vr.get("viewCountText").get("simpleText")
        vtitle = vr.get("title").get("runs")[0].get("text")
        results.append({
            "vid": vid,
            "vtitle": vtitle,
            "vcount": vcount,
            "vthumb": vthumb,
            "vduration": vduration
        })
    return results

if __name__ == "__main__":
    results = search_youtube("남박사")
    for r in results:
        print(r)
        print("=====================================")
