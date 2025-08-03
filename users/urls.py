from django.urls import path
from .views import proxy_check_user


from .views import (
    proxy_check_user,
    avatar_upload,
    avatar_delete,
    avatar_get,
)


urlpatterns = [
    path("proxy-check-user/", proxy_check_user),

    path('avatar/upload/', avatar_upload),
    path('avatar/delete/', avatar_delete),
    path('avatar/', avatar_get),
]