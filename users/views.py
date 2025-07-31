import requests
import json
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def proxy_check_user(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST requests allowed")

    try:
        data = json.loads(request.body)
        telegram_id = data.get("telegram_id")

        if not telegram_id:
            return JsonResponse({"success": False, "message": "telegram_id is required"}, status=400)

        api_url = "https://api.ayolclub.uz/en/api/v1/telegram-bot/check-user/"
        headers = {
            "X-API-Token": "ВАШ_СЕКРЕТНЫЙ_ТОКЕН"
        }
        payload = {
            "telegram_id": telegram_id
        }

        response = requests.post(api_url, json=payload, headers=headers, timeout=5)

        return JsonResponse(response.json(), status=response.status_code)

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
