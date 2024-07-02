import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import re

load_dotenv()
KBANK_API_KEY = os.getenv("KBANK_API_KEY")

CURRENCY_LIST = {
    "AED": {
        "country": "아랍에미리트",
        "aliases": "디르함, dirham"
    },
    "ATS": {
        "country": "오스트리아",
        "aliases": "실링, schilling"
    },
    "AUD": {
        "country": "호주",
        "aliases": "호주 달러, australian dollar"
    },
    "BEF": {
        "country": "벨기에",
        "aliases": "프랑, franc"
    },
    "BHD": {
        "country": "바레인",
        "aliases": "디나르, dinar"
    },
    "CAD": {
        "country": "캐나다",
        "aliases": "캐나다 달러, canadian dollar"
    },
    "CHF": {
        "country": "스위스",
        "aliases": "프랑, franc"
    },
    "CNH": {
        "country": "중국",
        "aliases": "위안화, yuan"
    },
    "DEM": {
        "country": "독일",
        "aliases": "마르크, mark"
    },
    "DKK": {
        "country": "덴마크",
        "aliases": "크로네, krone"
    },
    "ESP": {
        "country": "스페인",
        "aliases": "페세타, peseta"
    },
    "EUR": {
        "country": "유로존",
        "aliases": "유로, euro"
    },
    "FIM": {
        "country": "핀란드",
        "aliases": "마르카, markka"
    },
    "FRF": {
        "country": "프랑스",
        "aliases": "프랑, franc"
    },
    "GBP": {
        "country": "영국",
        "aliases": "파운드, pound"
    },
    "HKD": {
        "country": "홍콩",
        "aliases": "홍콩 달러, hong kong dollar"
    },
    "IDR": {
        "country": "인도네시아",
        "aliases": "루피아, rupiah"
    },
    "ITL": {
        "country": "이탈리아",
        "aliases": "리라, lira"
    },
    "JPY": {
        "country": "일본",
        "aliases": "엔, yen"
    },
    "KRW": {
        "country": "한국",
        "aliases": "원, won"
    },
    "KWD": {
        "country": "쿠웨이트",
        "aliases": "디나르, dinar"
    },
    "MYR": {
        "country": "말레이시아",
        "aliases": "링기트, ringgit"
    },
    "NLG": {
        "country": "네덜란드",
        "aliases": "길더, guilder"
    },
    "NOK": {
        "country": "노르웨이",
        "aliases": "크로네, krone"
    },
    "NZD": {
        "country": "뉴질랜드",
        "aliases": "뉴질랜드 달러, new zealand dollar"
    },
    "SAR": {
        "country": "사우디아라비아",
        "aliases": "리얄, riyal"
    },
    "SEK": {
        "country": "스웨덴",
        "aliases": "크로나, krona"
    },
    "SGD": {
        "country": "싱가포르",
        "aliases": "싱가포르 달러, singapore dollar"
    },
    "THB": {
        "country": "태국",
        "aliases": "바트, baht"
    },
    "USD": {
        "country": "미국",
        "aliases": "달러, 미국달러, 달라, dollar"
    },
    "XOF": {
        "country": "서아프리카",
        "aliases": "씨에프에이 프랑, cfa franc"
    }
}

def google_money_exchange_rate(search, to="원"):
    url = f"https://www.google.com/search?q={search}+{to}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    r = requests.get(url, headers=headers)
    bs = BeautifulSoup(r.text, "lxml")
    div = bs.find("div", attrs={"data-exchange-rate": True})
    if len(div) > 0:
        names = div.find_all("span", attrs={"data-name": True})
        money = div.find("span", attrs={"data-value": True})
        return (money.text, names[0].text, names[1].text)
    return (0, None, None)

def naver_money_exchange_rate(search, to="원"):
    url = f"https://search.naver.com/search.naver?where=nexearch&sm=top_hty&fbm=0&ie=utf8&query={search}+{to}"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    r = requests.get(url, headers=headers)
    bs = BeautifulSoup(r.text, "lxml")
    source = bs.select_one("span.nt_eng._code")
    target = bs.select_one("span.nb_txt._pronunciation")
    inputs = bs.select("input#num")
    if len(inputs) == 2:
        money = inputs[1].get("value")
        return (money, source.text, target.text)
    return (0, None, None)

def kbank_money_exchanage_rate_init():
    url = f"https://www.koreaexim.go.kr/site/program/financial/exchangeJSON?authkey={KBANK_API_KEY}&searchdate=20180102&data=AP01"
    r = requests.get(url)
    result = r.json()
    ouput = ""
    for item in result:
        cur_unit = item.get("cur_unit")
        cur_nm = item.get("cur_nm")
        deal_bas_r = item.get("deal_bas_r")
        CUR = CURRENCY_LIST.get(cur_unit)
        if CUR is not None:
            CUR.update({
                "deal_bas_r": deal_bas_r
            })

def money_exchange_rate(search, to=None):
    try:
        numbers = re.findall(r'\d+', search)[0]
        strings = re.findall(r'[^\d\s]+', search)[0]
    except:
        return (0, None, None)
    
    for key, value in CURRENCY_LIST.items():
        if strings in value.get("aliases"):
            dbr = value.get("deal_bas_r").replace(",", "")
            kor = float(dbr) * float(numbers)
        
            if to is None:
                return (kor, value.get("country"), value.get("country"))
            else:
                for k, v in CURRENCY_LIST.items():
                    if to in value.get("aliases"):
                        tbr = value.get("deal_bas_r")
                        key = value.get("country")
                        return (kor / float(tbr), key, key)
    return (0, None, None)

if __name__ == "__main__":
    kbank_money_exchanage_rate_init()
    print(money_exchange_rate("900달러"))
