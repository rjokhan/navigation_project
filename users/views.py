from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import UserProfile
import json


# ✅ Проверка пользователя по username или ID
@csrf_exempt
@require_POST
def check_user(request):
    try:
        body = json.loads(request.body)
        telegram_id = body.get("telegram_id", "").strip()

        if not telegram_id:
            return JsonResponse({"success": False, "message": "telegram_id не указан"}, status=400)

        # Удаляем @ в начале, если есть
        if telegram_id.startswith('@'):
            telegram_id = telegram_id[1:]

        # Поиск по username
        user = UserProfile.objects.filter(username=telegram_id).first()

        # Если не найдено, пробуем по ID
        if not user and telegram_id.isdigit():
            user = UserProfile.objects.filter(id=int(telegram_id)).first()

        if not user:
            return JsonResponse({"success": False, "message": f"Пользователь {telegram_id} не найден"}, status=404)

        return JsonResponse({
            "success": True,
            "user": {
                "name": user.name,
                "subscription_status": user.subscription_status,
                "city": user.city,
                "subscription_until": user.subscription_until,
            }
        })

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)}, status=500)
