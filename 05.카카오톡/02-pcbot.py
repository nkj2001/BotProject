import win32con, win32api, win32gui, ctypes, win32clipboard
import time
import re
from modules import weather
from modules import money_exchange_rate
_user32 = ctypes.WinDLL("user32")

CURRENCY_LIST = ["달러", "위안", "엔", "유로", "페소", "루블", "홍콩달러", "호주달러"]
def send_key(hwnd, keycode):
    win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, keycode, 0)
    time.sleep(0.01)
    win32api.PostMessage(hwnd, win32con.WM_KEYUP, keycode, 0)

def send_message(chatroom_name, text):
    hwndMain = win32gui.FindWindow(None, chatroom_name)
    hwndEdit = win32gui.FindWindowEx(hwndMain, None, "RichEdit50W", None)
    win32api.SendMessage(hwndEdit, win32con.WM_SETTEXT, 0, text)
    send_key(hwndEdit, win32con.VK_RETURN)

def open_chat(chat_name):
    hwndKakao = win32gui.FindWindow(None, "카카오톡")
    if hwndKakao:
        hwnd1 = win32gui.FindWindowEx(hwndKakao, None, "EVA_ChildWindow", None)
        hwnd2 = win32gui.FindWindowEx(hwnd1, None, "EVA_Window", None)
        hwndChatList = win32gui.FindWindowEx(hwnd1, hwnd2, "EVA_Window", None)
        print(f"{hex(hwndChatList)}")
        hwndEdit = win32gui.FindWindowEx(hwndChatList, None, "Edit", None)
        win32api.SendMessage(hwndEdit, win32con.WM_SETTEXT, 0, chat_name)
        time.sleep(0.5)
        send_key(hwndEdit, win32con.VK_RETURN)
        return True
    return False

def kakao_get_message(chatname):
    hwndMain = win32gui.FindWindow(None, chatname)
    if hwndMain:
        hwnd = win32gui.FindWindowEx(hwndMain, None, "EVA_VH_ListControl_Dblclk", None) 
        thread_id = _user32.GetWindowThreadProcessId(hwnd, None)
        lparam = win32api.MAKELONG(0, _user32.MapVirtualKeyA(ord('A'), 0))
        PBYTE = ctypes.c_ubyte * 256
        pKeyBuffers = PBYTE()
        pKeyBuffers_old = PBYTE()
        pKeyBuffers[win32con.VK_CONTROL] |= 128 #10000000

        _user32.AttachThreadInput(win32api.GetCurrentThreadId(), thread_id, True)
        _user32.GetKeyboardState(ctypes.byref(pKeyBuffers_old))
        _user32.SetKeyboardState(ctypes.byref(pKeyBuffers))

        time.sleep(0.01)
        win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, ord('A'), lparam)
        time.sleep(0.01)
        win32api.PostMessage(hwnd, win32con.WM_KEYUP, ord('A'), lparam | 0xC0000000)
        time.sleep(0.01)
        win32api.PostMessage(hwnd, win32con.WM_KEYDOWN, ord('C'), lparam)
        time.sleep(0.01)
        win32api.PostMessage(hwnd, win32con.WM_KEYUP, ord('C'), lparam | 0xC0000000)
        time.sleep(0.01)
        _user32.SetKeyboardState(ctypes.byref(pKeyBuffers_old))
        time.sleep(0.01)
        _user32.AttachThreadInput(win32api.GetCurrentThreadId(), thread_id, False)

        lparam = win32api.MAKELONG(10, 130)
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONDOWN, win32con.MK_LBUTTON, lparam)
        win32api.PostMessage(hwnd, win32con.WM_LBUTTONUP, win32con.MK_LBUTTON, lparam)
        time.sleep(0.5)
        data = copy_clipboard().split("\r\n")
        print(data)
        messages = []
        date = ""
        for d in data:
            if d.find("]") >= 0:
                _name = d[1:d.find("]")]
                d = d[d.find("]") + 1:].strip()
                _datetime = date + " " + d[1:d.find("]")]
                _msg = d[d.find("]") + 1:].strip()
                messages.append({
                    "name": _name,
                    "datetime": _datetime,
                    "msg": _msg
                })
            else:
                date = d
        return messages
    return []

def copy_clipboard():
    win32clipboard.OpenClipboard()
    data = win32clipboard.GetClipboardData()
    win32clipboard.CloseClipboard()
    return data

def main(chatname):
    last_message = ""
    my_message = ""
    while True:
        if open_chat(chatname):
            messages = kakao_get_message(chatname)
            if len(messages) > 0:
                message = messages[-1]
                msg = message.get("msg")
                if last_message == "":
                    last_message = msg
                if msg != last_message and msg != my_message:
                    match_money = re.search(f"^([0-9]+\s?)({"|".join(CURRENCY_LIST)})+$", msg)
                    match_weather = re.search("^([가-힣]{2})\s?날씨$", msg)
                    if match_money:
                        src = match_money.group()
                        result = money_exchange_rate.google_money_exchange_rate(src)
                        output = f"{result[1]} {result[0]} 원"
                    else:
                        output = f"{msg}에 대한 환율 정보 구하기 실패"
                    
                    if match_weather:
                        src = match_weather.group().replace("날씨", "")
                        w = weather.get_weather(src)
                        if w:
                            output = ""
                            for k, v in w.items():
                                output += f"{k}: {v}\r\n"
                        else:
                            output = f"{msg}에 대한 날씨 정보 구하기 실패"
                    
                    send_message(chatname, output)
                    my_message = output
                    last_message = msg
                time.sleep(1)
            else:
                print("메세지가 없습니다.")
        else:
            print("카카오톡이 실행중이 아닙니다.")

if __name__ == "__main__":
    chatname = "남박사"
    main(chatname)