import os
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json


AVATAR_FOLDER = os.path.join(settings.MEDIA_ROOT, 'avatars')


@csrf_exempt
def avatar_upload(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)

    telegram_id = request.POST.get('telegram_id')
    avatar_file = request.FILES.get('avatar')

    if not telegram_id or not avatar_file:
        return JsonResponse({'success': False, 'message': 'Missing data'}, status=400)

    # Определим расширение
    ext = avatar_file.name.split('.')[-1].lower()
    if ext not in ['jpg', 'jpeg', 'png', 'webp']:
        return JsonResponse({'success': False, 'message': 'Invalid image format'}, status=400)

    try:
        # Удаляем старую фотку, если есть
        for file_ext in ['jpg', 'jpeg', 'png', 'webp']:
            path = os.path.join(AVATAR_FOLDER, f"{telegram_id}.{file_ext}")
            if os.path.isfile(path):
                os.remove(path)

        # Сохраняем новую
        filename = f"{telegram_id}.{ext}"
        path = os.path.join(AVATAR_FOLDER, filename)
        default_storage.save(path, ContentFile(avatar_file.read()))

        return JsonResponse({
            'success': True,
            'avatar_url': f"{settings.MEDIA_URL}avatars/{filename}"
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)


def avatar_get(request):
    telegram_id = request.GET.get('telegram_id')
    if not telegram_id:
        return JsonResponse({'success': False, 'message': 'Missing telegram_id'}, status=400)

    for ext in ['jpg', 'jpeg', 'png', 'webp']:
        path = os.path.join(AVATAR_FOLDER, f"{telegram_id}.{ext}")
        if os.path.isfile(path):
            return JsonResponse({
                'success': True,
                'avatar_url': f"{settings.MEDIA_URL}avatars/{telegram_id}.{ext}"
            })

    return JsonResponse({'success': False, 'message': 'No avatar found'}, status=404)


@csrf_exempt
def avatar_delete(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Invalid method'}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        telegram_id = str(data.get('telegram_id'))

        for ext in ['jpg', 'jpeg', 'png', 'webp']:
            path = os.path.join(AVATAR_FOLDER, f"{telegram_id}.{ext}")
            if os.path.isfile(path):
                os.remove(path)

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)
