# navproject/urls.py  (корневой)
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path("admin/", admin.site.urls),

    # API
    path("api/", include("content.urls")),      # Контент/жанры/группы (JSON)
    path("api/users/", include("users.urls")),  # Проверка пользователя

    # HTML-страницы
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("content/", TemplateView.as_view(template_name="content.html"), name="content"),
    path("group/", TemplateView.as_view(template_name="group.html"), name="group"),  # ⬅️ ДОБАВЛЕНО
    path("group_content/", TemplateView.as_view(template_name="group_content.html"), name="group_content"),  # ⬅️ ДОБАВЛЕНО
    path("favourites/", TemplateView.as_view(template_name="favourited.html"), name="favourited"),
    path("profile/", TemplateView.as_view(template_name="profile.html"), name="profile"),
    path("searched/", TemplateView.as_view(template_name="searched.html"), name="searched"),
    path("chat/", TemplateView.as_view(template_name="chat.html"), name="chat"),
    path("rules/", TemplateView.as_view(template_name="rules.html"), name="rules"),
]

# Медиа и статика (dev)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG and getattr(settings, "STATICFILES_DIRS", None):
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
