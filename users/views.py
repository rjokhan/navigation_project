import requests
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def proxy_check_user(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST requests allowed")

    try:
        # Декодируем входящий JSON с явным указанием UTF-8
        data = json.loads(request.body.decode("utf-8"))
        telegram_id = str(data.get("telegram_id"))

        if not telegram_id:
            return JsonResponse({"success": False, "message": "telegram_id is required"}, status=400)

        # Подготовка запроса к внешнему API
        api_url = "https://api.ayolclub.uz/en/api/v1/telegram-bot/check-user/"
        headers = {
            "X-API-Token": "ВАШ_СЕКРЕТНЫЙ_ТОКЕН",
            "Content-Type": "application/json; charset=utf-8"
        }
        payload = json.dumps({"telegram_id": telegram_id}, ensure_ascii=False).encode("utf-8")

        # Отправка запроса
        response = requests.post(api_url, data=payload, headers=headers, timeout=5)

        # Возвращаем ответ от API
        return JsonResponse(response.json(), status=response.status_code)

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
