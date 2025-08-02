import requests

BOT_TOKEN = '7642180422:AAEdsxa29PYcTanwSKak8jLH8KzPhB8aXbY'  # вставь свой
CHANNEL_USERNAME = '@aclubopentest'  # или id канала, если он приватный

url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage'

payload = {
    "chat_id": CHANNEL_USERNAME,
    "text": "🔥 Новый контент от NAVIGATION\n\nОткрой мини-приложение прямо внутри Telegram 👇",
    "reply_markup": {
        "inline_keyboard": [
            [
                {
                    "text": "Открыть NAVIGATION",
                    "url": "https://t.me/nav_ayolclub_bot/navigation?startapp=inline"
                }
            ]
        ]
    },
    "parse_mode": "HTML"
}

response = requests.post(url, json=payload)

print("Status:", response.status_code)
print("Response:", response.text)
