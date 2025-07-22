from django.urls import path
from .views import check_user_view


urlpatterns = [
    path('check/', check_user_view, name='check-user'),
]
