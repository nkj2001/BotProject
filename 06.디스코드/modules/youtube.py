import requests
import json

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}

def youtube_music_info(url):
    header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
    r = requests.get(url, headers=header)
    p = "var ytInitialData = "
    idx_start = r.text.find(p)
    idx_end = r.text.find("};", idx_start + len(p))
    data =  r.text[idx_start + len(p) : idx_end + 1]
    _json = json.loads(data)
    panels = _json.get("engagementPanels")
    
    title_text = ""
    pub_date = ""
    view_count = ""
    vsubtitle = ""
    vsecondary_subtitle = ""

    for p in panels:
        content = p.get("engagementPanelSectionListRenderer", {}).get("content")
        if content is None:
            continue
        items = content.get("structuredDescriptionContentRenderer", {}).get("items")
        if items is None or len(items) == 0:
            continue

        for item in items:
            header_render = item.get("videoDescriptionHeaderRenderer")
            hcard_render = item.get("horizontalCardListRenderer")
            if header_render is not None:
                title_text = header_render.get("title", {}).get("runs")[0].get("text")
                pub_date = header_render.get("publishDate", {}).get("simpleText")
                view_count = header_render.get("views", {}).get("simpleText")
            if hcard_render is not None:
                cards = hcard_render.get("cards")
                for card in cards:
                    vmodel = card.get("videoAttributeViewModel")
                    if vmodel is None:
                        continue
                    vtitle = vmodel.get("title")
                    vsubtitle = vmodel.get("subtitle")
                    vsecondary_subtitle = vmodel.get("secondarySubtitle", {}).get("content")
    return {
        "title_text": title_text,
        "pub_date": pub_date,
        "view_count": view_count.replace("조회수", "").replace("회", "").replace(",", ""),
        "vtitle": vtitle,
        "vsubtitle": vsubtitle,
        "vsecondary_subtitle": vsecondary_subtitle
    }

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
