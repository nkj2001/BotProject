import requests
from bs4 import BeautifulSoup

def get_weather(keyword):
    url = f"https://www.weather.go.kr/w/renew2021/rest/main/place-search.do?query={keyword}&start=1&src=A2"
    r = requests.get(url)
    _json = r.json()
    _data = None
    for j in _json:
        address = j.get("address")
        if address.find(keyword) >= 0:
            _data = j
            break

    if _data:
        dong = _data.get("dongCode")
        url = f"https://www.weather.go.kr/w/wnuri-fct2021/main/current-weather.do?code={dong}"
        r = requests.get(url)
        bs = BeautifulSoup(r.text, "lxml")

        _span_tmp = bs.select_one("span.tmp")
        _span_minmax = _span_tmp.select("span.minmax > span")
        _min_temp = _span_minmax[1].text
        _max_temp = _span_minmax[3].text
        _span_tmp.span.decompose()
        _temp = _span_tmp.text

        _ic_hm = bs.select_one("span.ic-hm")
        _ic_hm_val = _ic_hm.parent.select_one("span.val").text
        _ic_wind = bs.select_one("span.ic-wind")
        _ic_wind_val = _ic_wind.parent.select_one("span.val").text

        _ic_rn = bs.select_one("span.ic-rn")
        _ic_rn_val = _ic_rn.parent.select_one("span.val").text

        _sunrise = bs.select_one("span.sunrise").parent.select("span")[1].text
        _sunset = bs.select_one("span.sunset").parent.select("span")[1].text

        _air_spans_v = bs.select("span.air-lvv")
        _air_spans_t = bs.select("span.air-lvt")

        for a in _air_spans_t:
            a.a.decompose()
        
        _air_levels = {
            "초미세먼지": f"{_air_spans_v[0].text}({_air_spans_t[0].text})",
            "미세먼지": f"{_air_spans_v[1].text}({_air_spans_t[1].text})",
            "오존": f"{_air_spans_v[2].text}({_air_spans_t[2].text})",
        }
        
        return {
            "기존": _temp,
            "최저": _min_temp,
            "최고": _max_temp,
            "습도": _ic_hm_val,
            "바람": _ic_wind_val,
            "강수량": _ic_rn_val,
            "일출": _sunrise,
            "일몰": _sunset,
            "대기질": _air_levels
        }
    return None

if __name__ == "__main__":
    print(get_weather("서울"))