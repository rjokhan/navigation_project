from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import Genre, ContentItem, Favourite
from django.shortcuts import render

import json




# ✅ Получение всех жанров и их контента
def genre_list(request):
    data = []
    for genre in Genre.objects.prefetch_related('items').all():
        genre_data = {
            'id': genre.id,
            'title': genre.title,
            'items': [
                {
                    'id': item.id,
                    'title': item.title,
                    'subtitle': item.subtitle,
                    'content_type': item.content_type,
                    'telegram_url': item.telegram_url,
                    'duration': item.duration,
                    'thumbnail': request.build_absolute_uri(item.thumbnail.url).replace('http://', 'https://') if item.thumbnail else None
                }
                for item in genre.items.order_by('-id')
            ]
        }
        data.append(genre_data)
    return JsonResponse(data, safe=False)


# ✅ Получение избранного контента по telegram_id
def get_favourites(request):
    telegram_id = request.GET.get('telegram_id')
    if not telegram_id:
        return JsonResponse({'error': 'Missing telegram_id'}, status=400)

    favourites = Favourite.objects.filter(telegram_id=telegram_id)
    fav_ids = [f.content_item.id for f in favourites]
    return JsonResponse({'favourites': fav_ids})


# ✅ Добавление в избранное
@csrf_exempt
@require_POST
def add_to_favourites(request, content_id):
    try:
        body = json.loads(request.body)
        telegram_id = body.get('telegram_id')
        if not telegram_id:
            return JsonResponse({'error': 'Missing telegram_id'}, status=400)

        content = get_object_or_404(ContentItem, id=content_id)
        Favourite.objects.get_or_create(telegram_id=telegram_id, content_item=content)
        return JsonResponse({'status': 'added'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ✅ Удаление из избранного
@csrf_exempt
@require_POST
def remove_from_favourites(request, content_id):
    try:
        body = json.loads(request.body)
        telegram_id = body.get('telegram_id')
        if not telegram_id:
            return JsonResponse({'error': 'Missing telegram_id'}, status=400)

        content = get_object_or_404(ContentItem, id=content_id)
        Favourite.objects.filter(telegram_id=telegram_id, content_item=content).delete()
        return JsonResponse({'status': 'removed'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



def searched_view(request):
    return render(request, "searched.html")