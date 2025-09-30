from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import get_object_or_404, render
from .models import Genre, ContentItem, Favourite, NewsItem, Group
import json


# ✅ Новости (What's New)
@require_GET
def news_list(request):
    try:
        limit = int(request.GET.get("limit", 5))
    except ValueError:
        limit = 5

    qs = NewsItem.objects.filter(is_active=True).order_by("order", "-created_at")[:limit]

    def abs_url(u: str) -> str:
        if not u:
            return ""
        if u.startswith("http://") or u.startswith("https://"):
            return u
        return request.build_absolute_uri(u)

    data = [
        {
            "image": abs_url(item.image.url if item.image else ""),
            "url": item.url or "",
            "title": item.title,
        }
        for item in qs
    ]
    return JsonResponse(data, safe=False)


# ✅ Получение всех жанров (спец или обычный)
@require_GET
def genre_list(request):
    data = []
    for genre in Genre.objects.all():
        data.append({
            "id": genre.id,
            "title": genre.title,
            "kind": getattr(genre, "kind", "regular"),  # regular / special
        })
    return JsonResponse(data, safe=False)


# ✅ Получение типа жанра
@require_GET
def genre_type(request, genre_id: int):
    g = get_object_or_404(Genre, id=genre_id)
    return JsonResponse({"genre_id": g.id, "genre_type": getattr(g, "kind", "regular"), "title": g.title})


# ✅ Контент выбранного жанра (с пагинацией и фильтром)
@require_GET
def content_list(request, genre_id: int):
    page = int(request.GET.get("page", 1))
    per_page = 20

    qs = ContentItem.objects.filter(genre_id=genre_id).order_by("-id")

    # фильтрация по типу
    ctype = request.GET.get("content_type")
    if ctype in ("video", "audio", "file"):
        qs = qs.filter(content_type=ctype)

    total = qs.count()
    start, end = (page - 1) * per_page, page * per_page
    items = qs[start:end]

    def abs_thumb(i):
        if not i.thumbnail:
            return None
        u = i.thumbnail.url
        return request.build_absolute_uri(u) if u.startswith("/") else u

    return JsonResponse({
        "genre_id": genre_id,
        "page": page,
        "per_page": per_page,
        "total": total,
        "items": [{
            "id": i.id,
            "title": i.title,
            "subtitle": i.subtitle,
            "content_type": i.content_type,
            "telegram_url": i.telegram_url,
            "duration": i.duration,
            "thumbnail": abs_thumb(i),
        } for i in items]
    })


# ✅ Список групп поджанра (для спецжанра)
@require_GET
def group_list(request, genre_id: int):
    g = get_object_or_404(Genre, id=genre_id)
    groups = g.groups.order_by("id").values("id", "title")
    return JsonResponse({
        "genre_id": g.id,
        "genre_type": getattr(g, "kind", "regular"),
        "title": g.title,
        "groups": list(groups),
    })


# ✅ Контент конкретной группы (с пагинацией и фильтром)
@require_GET
def group_content_list(request, group_id: int):
    page = int(request.GET.get("page", 1))
    per_page = 20

    qs = ContentItem.objects.filter(group_id=group_id).order_by("-id")

    ctype = request.GET.get("content_type")
    if ctype in ("video", "audio", "file"):
        qs = qs.filter(content_type=ctype)

    total = qs.count()
    start, end = (page - 1) * per_page, page * per_page
    items = qs[start:end]

    def abs_thumb(i):
        if not i.thumbnail:
            return None
        u = i.thumbnail.url
        return request.build_absolute_uri(u) if u.startswith("/") else u

    return JsonResponse({
        "group_id": group_id,
        "page": page,
        "per_page": per_page,
        "total": total,
        "items": [{
            "id": i.id,
            "title": i.title,
            "subtitle": i.subtitle,
            "content_type": i.content_type,
            "telegram_url": i.telegram_url,
            "duration": i.duration,
            "thumbnail": abs_thumb(i),
        } for i in items]
    })


# ✅ Получение избранного по telegram_id
def get_favourites(request):
    telegram_id = request.GET.get("telegram_id")
    if not telegram_id:
        return JsonResponse({"error": "Missing telegram_id"}, status=400)

    favourites = Favourite.objects.filter(telegram_id=telegram_id)
    fav_ids = [f.content_item.id for f in favourites]
    return JsonResponse({"favourites": fav_ids})


# ✅ Добавление в избранное
@csrf_exempt
@require_POST
def add_to_favourites(request, content_id):
    try:
        body = json.loads(request.body)
        telegram_id = body.get("telegram_id")
        if not telegram_id:
            return JsonResponse({"error": "Missing telegram_id"}, status=400)

        content = get_object_or_404(ContentItem, id=content_id)
        Favourite.objects.get_or_create(telegram_id=telegram_id, content_item=content)
        return JsonResponse({"status": "added"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ✅ Удаление из избранного
@csrf_exempt
@require_POST
def remove_from_favourites(request, content_id):
    try:
        body = json.loads(request.body)
        telegram_id = body.get("telegram_id")
        if not telegram_id:
            return JsonResponse({"error": "Missing telegram_id"}, status=400)

        content = get_object_or_404(ContentItem, id=content_id)
        Favourite.objects.filter(
            telegram_id=telegram_id, content_item=content
        ).delete()
        return JsonResponse({"status": "removed"})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ✅ Страница поиска
def searched_view(request):
    return render(request, "searched.html")
