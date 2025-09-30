from django.contrib import admin
from django.utils.html import format_html

from .models import Genre, Group, ContentItem, Favourite, UserProfile, NewsItem


# === Пользователи ===
@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["username", "name", "phone", "subscription_status", "city", "subscription_until"]
    search_fields = ["username", "name", "phone", "city"]
    list_filter = ["subscription_status", "city"]
    ordering = ["-subscription_until"]


# === Избранное ===
@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ["telegram_id", "content_item", "created_at"]
    search_fields = ["telegram_id", "content_item__title"]
    list_filter = ["created_at"]


# === Контент ===
@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    list_display = ["title", "genre", "group", "content_type"]
    search_fields = ["title", "subtitle"]
    list_filter = ["genre", "group", "content_type"]
    autocomplete_fields = ["genre", "group"]

    def get_fields(self, request, obj=None):
        fields = ["title", "subtitle", "genre", "group", "content_type", "telegram_url", "duration"]
        if obj is None or obj.content_type == "video":
            fields.append("thumbnail")
        return fields

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.content_type != "video":
            return ["thumbnail"]
        return []

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.content_type != "video" and "thumbnail" in form.base_fields:
            form.base_fields["thumbnail"].required = False
        return form


# === Жанры ===
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ["title", "kind"]
    list_filter = ["kind"]
    search_fields = ["title"]


# === Группы внутри спецжанров ===
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ["title", "genre"]
    list_filter = ["genre"]
    search_fields = ["title"]
    autocomplete_fields = ["genre"]


# === Новости (What's New) ===
@admin.register(NewsItem)
class NewsItemAdmin(admin.ModelAdmin):
    list_display = ("thumb", "title", "url", "is_active", "order", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "url")
    list_editable = ("is_active", "order")
    readonly_fields = ("preview",)
    ordering = ("order", "-created_at")

    fieldsets = (
        (None, {"fields": ("title", "url", "is_active", "order")}),
        ("Изображение", {"fields": ("image", "preview")}),
    )

    def thumb(self, obj):
        if not obj.image:
            return "—"
        return format_html('<img src="{}" style="height:36px;border-radius:6px;" />', obj.image.url)
    thumb.short_description = "Превью"

    def preview(self, obj):
        if not obj.image:
            return "—"
        return format_html('<img src="{}" style="max-width:420px;border-radius:10px;" />', obj.image.url)
    preview.short_description = "Предпросмотр"
