import os
import json
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from .models import UserProfile


@csrf_exempt
def proxy_check_user(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Only POST requests allowed")

    try:
        body = request.body.decode("utf-8")
        data = json.loads(body)
        telegram_id = str(data.get("telegram_id"))

        print(f"📥 Получен telegram_id: {telegram_id}")

        if not telegram_id:
            return JsonResponse({"success": False, "message": "telegram_id is required"}, status=400)

        api_url = "https://api.ayolclub.uz/en/api/v1/telegram-bot/check-user/"
        headers = {
            "X-API-Token": "b0e63095ee9d51fd0188f1877d63c0b850bc4965a61527c9",
            "Content-Type": "application/json; charset=utf-8",
            "Accept-Charset": "utf-8"
        }

        payload = json.dumps({"telegram_id": telegram_id}, ensure_ascii=False)
        response = requests.post(api_url, data=payload.encode("utf-8"), headers=headers, timeout=10)

        response.encoding = "utf-8"
        return JsonResponse(response.json(), status=response.status_code)

    except Exception as e:
        return JsonResponse({"success": False, "message": f"SERVER ERROR: {str(e)}"}, status=500)


@csrf_exempt
def avatar_upload(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)

    telegram_id = request.POST.get('telegram_id')
    avatar_file = request.FILES.get('avatar')

    if not telegram_id or not avatar_file:
        return JsonResponse({'success': False, 'message': 'Missing data'}, status=400)

    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)

        # удалить старую аву, если есть
        if profile.avatar and os.path.isfile(profile.avatar.path):
            os.remove(profile.avatar.path)

        # читаем содержимое и сохраняем с кастомным именем
        avatar_data = avatar_file.read()
        ext = avatar_file.name.split('.')[-1]
        filename = f"{telegram_id}_avatar.{ext}"

        profile.avatar.save(filename, ContentFile(avatar_data), save=True)

        return JsonResponse({'success': True, 'avatar_url': profile.avatar.url})

    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)


@csrf_exempt
def avatar_delete(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        telegram_id = str(data.get('telegram_id'))

        profile = UserProfile.objects.get(telegram_id=telegram_id)

        if profile.avatar and os.path.isfile(profile.avatar.path):
            os.remove(profile.avatar.path)

        profile.avatar = None
        profile.save()

        return JsonResponse({'success': True})

    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


def avatar_get(request):
    telegram_id = request.GET.get('telegram_id')
    if not telegram_id:
        return JsonResponse({'success': False, 'message': 'Missing telegram_id'}, status=400)

    try:
        profile = UserProfile.objects.get(telegram_id=telegram_id)
        if profile.avatar:
            return JsonResponse({'success': True, 'avatar_url': profile.avatar.url})
        else:
            return JsonResponse({'success': False, 'message': 'No avatar found'})
    except UserProfile.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
