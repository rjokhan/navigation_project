from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('content.urls')),        # Контент и жанры
    path('api/auth/', include('users.urls')),     # Регистрация, логин, логаут
    re_path(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),  # Только /
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
