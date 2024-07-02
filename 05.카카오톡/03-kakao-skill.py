from flask import Flask, request, jsonify
from modules import weather
from pprint import pprint

app = Flask(__name__)

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

@app.route("/test")
def test():
    return "OK"

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8763)