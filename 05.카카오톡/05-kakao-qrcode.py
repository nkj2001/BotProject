from flask import Flask, request, jsonify, send_from_directory
from modules import qrcode
from pprint import pprint
import urllib.request
import cv2
app = Flask(__name__)

@app.route("/qrcode_encode", methods=["POST"])
def qrcode_encode():
    content = request.get_json()
    pprint(content)
    url = content.get("action").get("detailParams").get("URL").get("origin")
    qr_image = qrcode.QRCreater().make(url).png()
    filename = qr_image.split("\\")[-1]
    qr_url = f"http://123.123.123.123:8763/image/{filename}"
    return jsonify({
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleImage": {
                        "altText": "큐알코드",
                        "imageUrl": qr_url
                    }
                }
            ],
        }
    })

@app.route("/image/<path:file>")
def get_image(file):
    return send_from_directory("modules", file)

@app.route("/qrcode_decode", methods=["POST"])
def qrcode_decode():
    content = request.get_json()
    pprint(content)
    image = content.get("action").get("detailParams").get("이미지")
    image_list = image.get("origin")
    if image_list[0:4] == "List":
        image_list = image_list[5:-1].split(",")
    output = ""
    for img in image_list:
        urllib.request.urlretrieve(img, "qr.png")
        cv_image = cv2.imread("qr.png")
        if cv_image is not None:
            result = qrcode.read_qrcode_zbar(cv_image)
            output += f"{result[0].get('data')}\n"
        else:
            output += "QR코드를 찾을 수 없습니다.\n"
    return jsonify({
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
    })

@app.route("/qrcode", methods=["POST"])
def get_qrcode():
    result_json = {
        "version": "2.0",
        "template": {
            "outputs": [
                {
                    "simpleText": {
                        "text": "메뉴를 선택하세요."
                    }
                }
            ],
            "quickReplies": [
                {
                    "action": "block",
                    "blockId": "662582df1c7add17b7d094df",
                    "label": "QR코드 해석하기"
                },
                {
                    "action": "block",
                    "blockId": "662582d47e38b92310024053",
                    "label": "QR코드 만들기"
                }
            ]
        }
    }
    return jsonify(result_json)

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8763)