from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('content.urls')),        # Контент и жанры
    path('api/auth/', include('users.urls')),     # Регистрация, логин, логаут

    # Основные HTML-страницы
    re_path(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    path('favourites/', TemplateView.as_view(template_name='favourited.html'), name='favourited'),
    path('profile/', TemplateView.as_view(template_name='profile.html'), name='profile'),
    path('searched/', TemplateView.as_view(template_name='searched.html'), name='searched'),
    path('chat/', TemplateView.as_view(template_name='chat.html'), name='chat'),


    # Если в будущем появится chat.html, можно добавить:
    # path('chat/', TemplateView.as_view(template_name='chat.html'), name='chat'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
