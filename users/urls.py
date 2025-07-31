from django.urls import path
from .views import proxy_check_user

urlpatterns = [
    path("proxy-check-user/", proxy_check_user),
]
