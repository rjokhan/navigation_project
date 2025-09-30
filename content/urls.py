# content/urls.py
from django.urls import path
from .views import (
    news_list,
    genre_list,
    genre_type,
    content_list,
    group_list,
    group_content_list,
    get_favourites,
    add_to_favourites,
    remove_from_favourites,
    searched_view,
)

urlpatterns = [
    # Новости
    path("news/", news_list, name="news_list"),

    # Жанры
    path("genres/", genre_list, name="genre_list"),
    path("genres/<int:genre_id>/type/", genre_type, name="genre_type"),

    # Контент жанра (с пагинацией и фильтром)
    path("genres/<int:genre_id>/content/", content_list, name="content_list"),

    # Группы (только для спецжанров)
    path("genres/<int:genre_id>/groups/", group_list, name="group_list"),
    path("groups/<int:group_id>/content/", group_content_list, name="group_content_list"),

    # Избранное
    path("favourites/", get_favourites, name="get_favourites"),
    path("favourites/add/<int:content_id>/", add_to_favourites, name="add_favourite"),
    path("favourites/remove/<int:content_id>/", remove_from_favourites, name="remove_favourite"),

    # Поиск
    path("searched/", searched_view, name="searched"),
]
