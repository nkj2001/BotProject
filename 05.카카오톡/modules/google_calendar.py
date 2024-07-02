import jwt
import time
import requests
from datetime import datetime, timedelta

def get_jwt():
    private_key_id = "-----------------------"
    private_key = "-----BEGIN PRIVATE KEY-----\n-----END PRIVATE KEY-----\n"
    service_account = "----------------------"
    iat = time.time()
    exp = iat + 3600
    payload = {
        "iss": service_account,
        "sub": service_account,
        "scope": "https://www.googleapis.com/auth/calendar \
                https://www.googleapis.com/auth/calendar.events",
        "aud": "https://oauth2.googleapis.com/token",
        "iat": iat,
        "exp": exp
    }
    header = {"kid": private_key_id}
    _jwt = jwt.encode(payload, private_key, headers=header, algorithm="RS256")
    return _jwt

def get_access_token():
    _jwt = get_jwt()
    url = "https://www.googleapis.com/oauth2/v4/token"
    data = {
        "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
        "assertion": _jwt
    }
    r = requests.post(url, data=data)
    return r.json().get("access_token")

def get_calendar_events(timeMin=None, timeMax=None):
    access_token = get_access_token()
    if access_token is None:
        return []
    
    c_id = "xxxx@gmail.com"
    url = f"https://www.googleapis.com/calendar/v3/calendars/{c_id}/events?timeZone=Asia/Seoul"

    if timeMin is not None:
        if isinstance(timeMin, str):
            timeMin = datetime.strptime(timeMin, "%Y-%m-%d")
        timeMin -= timedelta(hours=9)
        url += f"&timeMin={timeMin.isoformat("T")}Z"
    
    if timeMax is not None:
        if isinstance(timeMax, str):
            timeMax = datetime.strptime(timeMax, "%Y-%m-%d")
        timeMax -= timedelta(hours=9)
        url += f"&timeMax={timeMax.isoformat("T")}Z"

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token
    }
    
    r = requests.get(url, headers=headers)
    print(r.text)
    _items = r.json().get("items")
    return _items

def insert_event(summary, colorId="2", start_date=None, end_date=None, location=None, description=None):
    c_id = "xxxx@gmail.com"
    access_token = get_access_token()
    if access_token is None:
        return None
    if start_date is not None and end_date is None:
        print("시작날짜와 종료날짜는 함께 설정 되어야 합니다.")
        return None
    
    if start_date is not None and end_date is not None:
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, "%Y-%m-%d %H:%M")
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, "%Y-%m-%d %H:%M")
    
    event_data = {
        "summary": summary,
        "colorId": colorId,
        "recurrence": ["RRULE:FREQ=DAILY;COUNT=1"],
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "email", "minutes": 24 * 60},
                {"method": "popup", "minutes": 10},
            ]
        }
    }

    if start_date is not None and end_date is not None:
        event_data.update({
            "start": {"dateTime": str(start_date.isoformat("T")), "timeZone": "Asia/Seoul"},
            "end": {"dateTime": str(end_date.isoformat("T")), "timeZone": "Asia/Seoul"},
        })
    if location is not None:
        event_data.update({"location": location})
    if description is not None:
        event_data.update({"description": description})
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token
    }

    url = f"https://www.googleapis.com/calendar/v3/calendars/{c_id}/events"
    r = requests.post(url, headers=headers, json=event_data)
    print(r.text)
    return r.json()

def delete_event(event_id):
    access_token = get_access_token()
    if access_token is None or event_id is None:
        return False
    c_id = "xxxx@gmail.com"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + access_token
    }
    url = f"https://www.googleapis.com/calendar/v3/calendars/{c_id}/events/{event_id}"
    r = requests.delete(url, headers=headers)
    if r.status_code == 204:
        return True
    return False
