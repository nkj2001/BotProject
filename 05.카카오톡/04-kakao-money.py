from flask import Flask, request, jsonify
from modules import money_exchange_rate
from pprint import pprint
import re

app = Flask(__name__)

CURRENCY_LIST = ["달러", "위안", "엔", "유로", "페소", "루블", "홍콩달러", "호주달러"]

def convert_korea_to_number(input_string):
    input_string = input_string.replace(",", "")
    unit_map = {
        "만": 10000,
        "억": 100000000,
        "조": 1000000000000
    }
    pattern = re.compile(r"(\d+)(만|억|조)?원")
    match = pattern.search(input_string)
    if match:
        number = int(match.group(1))
        unit = match.group(2)
        if unit and unit in unit_map:
            return number * unit_map[unit]
        else:
            return number
    return None

@app.route("/exchange_from_won", methods=["POST"])
def get_exchange_from_won():
    content = request.get_json()
    pprint(content)
    utterance = content.get("userRequest").get("utterance")
    #match1 = re.search(f"([0-9]+\s?원)", utterance)
    pattern = r"(\d{1,3}(?:,\d{3})*[만억조]?원)|(\d+[만억조]?원)|([영일이삼사오육칠팔구십백천만억조경]+원)"
    match1 = re.search(pattern, utterance)
    match2 = re.search(f"({'|'.join(CURRENCY_LIST)})", utterance)
    print(match1, match2)
    korea_won = convert_korea_to_number(match1.group())
    quick = []
    if match1 and match2:
        money, source, target = money_exchange_rate.google_money_exchange_rate(korea_won, match2.group())
        output = f"{money} {target}"
    else:
        output = "통화를 선택하세요."
        for c in CURRENCY_LIST:
            quick.append({
                "action": "message",
                "messageText": f"{match1.group()} {c}",
                "label": f"{c}"
            })
        
    result_json = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": output
                    }
                }
            ],
        }
    }
    if len(quick) > 0:
        result_json["template"]["quickReplies"] = quick
    
    return jsonify(result_json)
    
@app.route("/exchange_to_won", methods=["POST"])
def get_exchange_to_won():
    content = request.get_json()
    pprint(content)
    utterance = content.get("userRequest").get("utterance")
    match = re.search(f"([0-9]+\s?)({'|'.join(CURRENCY_LIST)})+$", utterance)
    if match:
        money, source, target = money_exchange_rate.google_money_exchange_rate(match.group(), "원")
        output = f"{money} {target}"
    else:
        output = "지원하지 않는 화폐 입니다."
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

@app.route("/weather", methods=["POST"])
def get_weather():
    content = request.get_json()
    pprint(content)
    intent = content.get("intent")
    action = content.get("action")
    sys_location = "서울"
    if action:
        if action.get("detailParams").get("sys_location") is not None:
            sys_location = action.get("detailParams").get("sys_location").get("origin")
    results = weather.get_weather(sys_location)
    output = ""
    for k, v in results.items():
        output += f"{k}: {v}\n"
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