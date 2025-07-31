import requests
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def proxy_check_user(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST requests allowed")

    try:
        body = request.body.decode("utf-8")
        data = json.loads(body)
        telegram_id = str(data.get("telegram_id"))

        print(f"📥 Получен telegram_id: {telegram_id}")  # лог в консоль

        if not telegram_id:
            return JsonResponse({"success": False, "message": "telegram_id is required"}, status=400)

        # Подготовка запроса
        api_url = "https://api.ayolclub.uz/en/api/v1/telegram-bot/check-user/"
        headers = {
            "X-API-Token": "ВАШ_ТОКЕН",
            "Content-Type": "application/json; charset=utf-8",
            "Accept-Charset": "utf-8"
        }

        payload = json.dumps({"telegram_id": telegram_id}, ensure_ascii=False)
        print(f"📤 Payload: {payload}")  # лог JSON

        response = requests.post(api_url, data=payload.encode("utf-8"), headers=headers, timeout=10)

        print(f"✅ Ответ API [{response.status_code}]: {response.text}")  # лог ответа

        response.encoding = "utf-8"
        return JsonResponse(response.json(), status=response.status_code)

    except Exception as e:
        print(f"❌ SERVER ERROR: {e}")  # лог ошибки в консоль
        return JsonResponse({"success": False, "message": f"SERVER ERROR: {str(e)}"}, status=500)
