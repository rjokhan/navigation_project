import requests
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import User  # твоя модель User, если она есть

API_URL = "https://api.ayolclub.uz/en/api/v1/telegram-bot/check-user/"
API_TOKEN = "b0e63095ee9d51fd0188f1877d63c0b850bc4965a61527c9"

@csrf_exempt
def check_user_view(request):
    """
    Получает telegram_id от клиента, проверяет через внешний API,
    и возвращает либо success, либо redirect.
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'Method not allowed'}, status=405)

    telegram_id = request.POST.get('telegram_id')
    if not telegram_id:
        return JsonResponse({'success': False, 'message': 'Missing telegram_id'}, status=400)

    headers = {
        'X-API-Token': API_TOKEN,
    }
    payload = {
        'telegram_id': telegram_id
    }

    response = requests.post(API_URL, headers=headers, data=payload)

    if response.status_code != 200:
        return JsonResponse({'success': False, 'message': 'API error'}, status=502)

    result = response.json()

    if result.get('success'):
        # можно расширить: сохранить пользователя в БД, если надо
        return JsonResponse({'success': True, 'message': 'Access granted'})
    else:
        return JsonResponse({'success': False, 'message': 'User not found'})
