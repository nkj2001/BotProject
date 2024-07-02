import pyqrcodeng as qrcode
import os
from uuid import uuid4
import pyzbar.pyzbar as pyzbar
import cv2

class QRCreater():
    def __init__(self):
        self.q = None
        self.module_color = (0, 0, 0, 0)
        self.back_color = (255, 255, 255, 255)
        self.scale = 5
    
    def get_base64(self):
        if self.q is not None:
            return self.q.png_data_uri(module_color=self.module_color, background=self.back_color, scale=self.scale)
        return None
        
    def qrcode_namecard(self, name, tel, email=None, url=None, org=None, title=None):
        vcard = f"BEGIN:VCARD\n"
        vcard += f"VERSION:4.0\n"
        vcard += f"FN:{name}\n"
        vcard += f"TEL;TYPE=WORK;CELL:{tel}\n"

        if org is not None:
            vcard += f"ORG:{org}\n"
        if title is not None:
            vcard += f"TITLE:{title}\n"
        if email is not None:
            vcard += f"EMAIL;TYPE=WORK:{email}\n"
        if url is not None:
            vcard += f"URL:{url}\n"

        vcard += "END:VCARD\n"

        self.q = qrcode.create(vcard, encoding="utf-8")
        return self

    def qrcode_wifi(self, ssid, encrypt, password):
        data = f"WIFI:S:{ssid};T:{encrypt};P:{password}"
        self.q = qrcode.create(data, encoding="utf-8")
        return self

    def qrcode_sms(self, sendto, msg):
        data = f"SMSTO:{sendto}:{msg}"
        self.q = qrcode.create(data, encoding="utf-8")
        return self

    def qrcode_email(self, email, subject, body):
        data = f"MATMSG:TO:{email};SUB:{subject};BODY:{body};;"
        self.q = qrcode.create(data, encoding="utf-8")
        return self

    def qrcode_geo(self, lon, lat):
        data = f"GEO:{lon},{lat}?z=10"
        self.q = qrcode.create(data, encoding="utf-8")
        return self
    
    def make(self, data):
        self.q = qrcode.create(data, encoding="utf-8")
        return self

    def png(self):
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        filename = f"{cur_dir}\\{uuid4()}.png"
        self.q.png(filename, scale=5)
        return filename

def read_qrcode_zbar(opencv_image):
    gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
    decoded = pyzbar.decode(gray)
    results = []
    for d in decoded:
        qr_data = d.data.decode("utf-8")
        qr_type = d.type

        results.append({
            "data": qr_data,
            "type": qr_type
        })
    return results