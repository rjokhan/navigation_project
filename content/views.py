from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import get_object_or_404, render
from django.db.models import Count
from .models import Genre, ContentItem, Favourite, NewsItem, Group
import json


# ---- helpers ---------------------------------------------------------------

def _abs_url(request, url: str) -> str:
    """Собрать абсолютный URL для медиа/картинок, если пришёл относительный путь."""
    if not url:
        return ""
    if url.startswith("http://") or url.startswith("https://"):
        return url
    return request.build_absolute_uri(url)


def _abs_thumb(request, item: ContentItem):
    if not item.thumbnail:
        return None
    u = item.thumbnail.url
    return _abs_url(request, u)


def _get_page(param_value, default=1):
    try:
        p = int(param_value or default)
        return p if p > 0 else default
    except (TypeError, ValueError):
        return default


# ✅ Новости (What's New)
@require_GET
def news_list(request):
    try:
        limit = int(request.GET.get("limit", 5))
    except ValueError:
        limit = 5

    qs = NewsItem.objects.filter(is_active=True).order_by("order", "-created_at")[:limit]

    data = [
        {
            "image": _abs_url(request, item.image.url if item.image else ""),
            "url": item.url or "",
            "title": item.title,
        }
        for item in qs
    ]
    return JsonResponse(data, safe=False)


# ✅ Получение всех жанров (спец или обычный)
@require_GET
def genre_list(request):
    data = [
        {
            "id": genre.id,
            "title": genre.title,
            "kind": getattr(genre, "kind", "regular"),  # default/special
        }
        for genre in Genre.objects.all()
    ]
    return JsonResponse(data, safe=False)


# ✅ Получение типа жанра
@require_GET
def genre_type(request, genre_id: int):
    g = get_object_or_404(Genre, id=genre_id)
    return JsonResponse({
        "genre_id": g.id,
        "genre_type": getattr(g, "kind", "regular"),
        "title": g.title
    })


# ✅ Контент выбранного жанра (с пагинацией и фильтром)
@require_GET
def content_list(request, genre_id: int):
    page = _get_page(request.GET.get("page"), default=1)
    per_page = 20

    qs = ContentItem.objects.filter(genre_id=genre_id).order_by("-id")

    # фильтрация по типу
    ctype = request.GET.get("content_type")
    if ctype in ("video", "audio", "file"):
        qs = qs.filter(content_type=ctype)

    total = qs.count()
    start, end = (page - 1) * per_page, page * per_page
    items = qs[start:end]

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
            "thumbnail": _abs_thumb(request, i),
        } for i in items]
    })


# ✅ Список групп спецжанра (расширено под референс)
@require_GET
def group_list(request, genre_id: int):
    g = get_object_or_404(Genre, id=genre_id)
    # берём группы и сразу подтягиваем количество items
    groups_qs = (
        g.groups
        .annotate(items_count=Count("items"))
        .order_by("id")
    )

    groups = []
    for gr in groups_qs:
        cover_url = _abs_url(request, gr.cover.url) if getattr(gr, "cover", None) else ""
        groups.append({
            "id": gr.id,
            "title": gr.title,
            "description": getattr(gr, "description", "") or "",
            "expert": getattr(gr, "expert", "") or "",
            "cover": cover_url,
            "items_count": gr.items_count,
        })

    return JsonResponse({
        "genre_id": g.id,
        "genre_type": getattr(g, "kind", "regular"),
        "title": g.title,
        "groups": groups,
    })


# ✅ Контент конкретной группы (с пагинацией и фильтром)
@require_GET
def group_content_list(request, group_id: int):
    page = _get_page(request.GET.get("page"), default=1)
    per_page = 20

    qs = ContentItem.objects.filter(group_id=group_id).order_by("-id")

    ctype = request.GET.get("content_type")
    if ctype in ("video", "audio", "file"):
        qs = qs.filter(content_type=ctype)

    total = qs.count()
    start, end = (page - 1) * per_page, page * per_page
    items = qs[start:end]

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
            "thumbnail": _abs_thumb(request, i),
        } for i in items]
    })


# ✅ Получение избранного по telegram_id
@require_GET
def get_favourites(request):
    telegram_id = request.GET.get("telegram_id")
    if not telegram_id:
        return JsonResponse({"error": "Missing telegram_id"}, status=400)

    favourites = Favourite.objects.filter(telegram_id=telegram_id).select_related("content_item")
    fav_ids = [f.content_item_id for f in favourites]
    return JsonResponse({"favourites": fav_ids})


# ✅ Добавление в избранное
@csrf_exempt
@require_POST
def add_to_favourites(request, content_id):
    try:
        body = json.loads(request.body or "{}")
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
        body = json.loads(request.body or "{}")
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


# ✅ (HTML) Страница групп спецжанра — под референс
#    Подключи в urls.py, например:
#    path("group/", views.group_page, name="group_page"),
def group_page(request):
    """
    Рендерит HTML-шаблон страницы списка групп для спецжанра.
    Ожидаются query-параметры: ?genre_id=...&genre_title=...
    Дальше фронт сам ходит в /api/groups/<genre_id>/ и рисует карточки.
    """
    return render(request, "group.html")


def group_content_page(request):
    """
    HTML-страница контента конкретной группы.
    Ожидает query-параметры: ?group_id=...&group_title=... (и опционально genre_*).
    Дальше фронт сам дергает /api/group/<group_id>/ и отрисовывает карточки.
    """
    return render(request, "group_content.html")
