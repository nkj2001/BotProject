import requests
from bs4 import BeautifulSoup

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}

def search_movie_daum(keyword):
    url = f"https://search.daum.net/search?w=cin&q={keyword}&DA=EM1&rtmaxcoll=EM1&irt=movie-single-tab"
    r = requests.get(url, headers=header)
    bs = BeautifulSoup(r.text, "lxml")
    c = bs.select_one("c-container")
    c_title = c.select_one("c-title")
    c_content = c.select_one("c-doc-content")
    c_thumb = c_content.select_one("c-thumb")
    c_list = c_content.select_one("c-list-grid-desc")
    c_dt = c_list.select("dt")
    c_dd = c_list.select("dd")
    c_data = {}
    for dt, dd in zip(c_dt, c_dd):
        d_text = dt.contents[0]
        d_val = dd.contents[0]
        c_data[d_text.strip()] = d_val.strip()
    
    return {
        "title": c_title.contents[0],
        "thumbnail": c_thumb.get("data-original-src"),
        "info": c_data
    }

if __name__ == "__main__":
    print(search_movie_daum("아바타"))