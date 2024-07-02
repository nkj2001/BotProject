import requests
import json

def save_auth_to_json():
    url = "https://kauth.kakao.com/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": "------------",
        "redirect_uri": "http://localhost:9999",
        "code": "35Ni-------------------------"
    }
    response = requests.post(url, data=data)
    token = response.json()
    with open("token.json", "w", encoding="utf-8") as f:
        json.dump(token, f)

def load_json():
    with open("token.json", "r", encoding="utf-8") as f:
        token = json.load(f)
    return token

def refresh_token(tokens):
    r_token = tokens.get("refresh_token")
    if r_token is not None:
        url = "https://kauth.kakao.com/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": "726b679dc3858e6f246e2c6c548a4544",
            "refresh_token": r_token
        }
        response = requests.post(url, data=data)
        receive_token = response.json()
        for k, v in receive_token.items():
            tokens[k] = v
        with open("token.json", "w", encoding="utf-8") as f:
            json.dump(tokens, f)
    return tokens

def send_message():
    tokens = refresh_token(load_json())
    access_token = tokens.get("access_token")
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": "테스트 메세지",
            "link": {
                "web_url": "https://blog.naver.com/nkj2001"
            }
        })
    }
    r = requests.post(url, headers=headers, data=data)
    if r.json().get("result_code") == 0:
        print("전송 성공!!")
    else:
        print(f"전송 실패: {str(r.json())}")

def send_location():
    tokens = refresh_token(load_json())
    access_token = tokens.get("access_token")
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "template_object": json.dumps({
            "object_type": "location",
            "text": "테스트 위치정보 입니다.\n테스트 메세지",
            "address": "경기 성남시 분당구 판교역로 235",
            "content": {
                "title": "지도보기",
                "image_url": "https://cdn.pixabay.com/photo/2018/04/13/16/35/earth-3316984_960_720.png",
                "image_width": 960,
                "image_height": 720,
                "link": {
                    "web_url": ""
                }
            }
        })
    }
    r = requests.post(url, headers=headers, data=data)
    if r.json().get("result_code") == 0:
        print("전송 성공!!")
    else:
        print(f"전송 실패: {str(r.json())}")

#save_auth_to_json()
#send_message()
send_location()