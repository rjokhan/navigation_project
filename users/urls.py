from django.urls import path
from .views import (
    proxy_check_user,
    avatar_upload,
    avatar_delete,
    avatar_get,
    avatar_upload_simple,
    avatar_get_simple,
)

urlpatterns = [
    path("proxy-check-user/", proxy_check_user),

    # Старая логика с UserProfile
    path("avatar/upload/", avatar_upload),
    path("avatar/delete/", avatar_delete),
    path("avatar/", avatar_get),

    # Новая простая логика без UserProfile (работа с файлами напрямую)
    path("avatar-simple/upload/", avatar_upload_simple),
    path("avatar-simple/", avatar_get_simple),
]
