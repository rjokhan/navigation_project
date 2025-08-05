import os
import json
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import UserProfile
from django.core.files.base import ContentFile

# Папка для хранения простых аватаров (без модели)
AVATAR_FOLDER = os.path.join(settings.MEDIA_ROOT, 'avatars')
os.makedirs(AVATAR_FOLDER, exist_ok=True)


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

        if profile.avatar and os.path.isfile(profile.avatar.path):
            os.remove(profile.avatar.path)

        profile.avatar = avatar_file
        profile.save()

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


# === Новая простая логика загрузки и получения аватара без UserProfile ===

@csrf_exempt
def avatar_upload_simple(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)

    telegram_id = request.POST.get('telegram_id')
    avatar_file = request.FILES.get('avatar')

    if not telegram_id or not avatar_file:
        return JsonResponse({'success': False, 'message': 'Missing data'}, status=400)

    ext = avatar_file.name.split('.')[-1].lower()
    if ext not in ['jpg', 'jpeg', 'png', 'webp']:
        return JsonResponse({'success': False, 'message': 'Invalid image format'}, status=400)

    try:
        # Удаляем старую версию с любым расширением
        for file_ext in ['jpg', 'jpeg', 'png', 'webp']:
            path = os.path.join(AVATAR_FOLDER, f"{telegram_id}.{file_ext}")
            if os.path.isfile(path):
                os.remove(path)

        filename = f"{telegram_id}.{ext}"
        path = os.path.join(AVATAR_FOLDER, filename)

        with open(path, 'wb+') as destination:
            for chunk in avatar_file.chunks():
                destination.write(chunk)

        return JsonResponse({
            'success': True,
            'avatar_url': f"{settings.MEDIA_URL}avatars/{filename}"
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


def avatar_get_simple(request):
    telegram_id = request.GET.get('telegram_id')
    if not telegram_id:
        return JsonResponse({'success': False, 'message': 'Missing telegram_id'}, status=400)

    for ext in ['jpg', 'jpeg', 'png', 'webp']:
        filename = f"{telegram_id}.{ext}"
        path = os.path.join(AVATAR_FOLDER, filename)
        if os.path.isfile(path):
            return JsonResponse({
                'success': True,
                'avatar_url': f"{settings.MEDIA_URL}avatars/{filename}"
            })

    return JsonResponse({'success': False, 'message': 'No avatar found'}, status=404)
