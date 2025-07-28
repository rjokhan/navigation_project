from django.urls import path
from .views import check_user

urlpatterns = [
    path('check/', check_user, name='check_user'),
]
