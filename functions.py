import hashlib
import time
import sqlite3
import qrcode
from io import BytesIO
import base64
import requests

def get_external_ip():
    try:
        response = requests.get('https://icanhazip.com/')
        if response.status_code == 200:
            return response.text.strip()
    except requests.RequestException as e:
        print(f"Error fetching external IP: {e}")
    return None

def generate_unique_link_id(user_id, original_url):
    timestamp = int(time.time())
    hash_input = f"{user_id}{original_url}{timestamp}".encode('utf-8')
    link_id = hashlib.sha256(hash_input).hexdigest()[:10]
    return link_id

def generate_qr_code(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')
    img_bytes = BytesIO()
    img.save(img_bytes)
    img_bytes.seek(0)
    img_base64 = base64.b64encode(img_bytes.getvalue()).decode('utf-8')
    return img_base64


def send_data_to_google_analytics(user_id):
    measurement_id = 'G-QPEN0SXB39'
    api_secret = 'xI94aAJATUCH6u36lcamNw'
    base_url = 'https://www.google-analytics.com/mp/collect'
    client_id = user_id 

    data = {
        "client_id": client_id,
        "events": [{
            "name": "page_view"
        }]
    }

    requests.post(f"{base_url}?measurement_id={measurement_id}&api_secret={api_secret}", json=data)

