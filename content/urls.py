from django.urls import path
from .views import (
    genre_list,
    get_favourites,
    add_to_favourites,
    remove_from_favourites,
)

urlpatterns = [
    # 🔹 Получение жанров и контента
    path('genres/', genre_list, name='genre_list'),

    # 🔹 Работа с избранным
    path('favourites/', get_favourites, name='get_favourites'),
    path('favourites/add/<int:content_id>/', add_to_favourites, name='add_favourite'),
    path('favourites/remove/<int:content_id>/', remove_from_favourites, name='remove_favourite'),
]
