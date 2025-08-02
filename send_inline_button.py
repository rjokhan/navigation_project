import requests

BOT_TOKEN = '7642180422:AAEdsxa29PYcTanwSKak8jLH8KzPhB8aXbY'
CHANNEL_ID = '-1002895736022'  # формат для закрытых каналов
URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

payload = {
    "chat_id": CHANNEL_ID,
    "text": "Открыть NAVIGATION в inline-режиме",
    "reply_markup": {
        "inline_keyboard": [
            [
                {
                    "text": "Перейти в NAVIGATION",
                    "web_app": {
                        "url": "https://navigation.ayolclub.uz/"
                    }
                }
            ]
        ]
    }
}

response = requests.post(URL, json=payload)
print("Status:", response.status_code)
print("Response:", response.text)
