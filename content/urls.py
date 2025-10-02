# content/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ✅ Новости
    path("news/", views.news_list, name="news_list"),

    # ✅ Жанры
    path("genres/", views.genre_list, name="genre_list"),
    path("genre/<int:genre_id>/type/", views.genre_type, name="genre_type"),

    # ✅ Контент жанра (с пагинацией и фильтром)
    path("content/<int:genre_id>/", views.content_list, name="content_list"),

    # ✅ Группы и контент групп
    path("groups/<int:genre_id>/", views.group_list, name="group_list"),
    path("group/<int:group_id>/", views.group_content_list, name="group_content_list"),

    # ✅ Избранное
    path("favourites/", views.get_favourites, name="get_favourites"),
    path("favourites/add/<int:content_id>/", views.add_to_favourites, name="add_to_favourites"),
    path("favourites/remove/<int:content_id>/", views.remove_from_favourites, name="remove_from_favourites"),

    # ✅ Поиск (HTML-страница)
    path("searched/", views.searched_view, name="searched_view"),
]
