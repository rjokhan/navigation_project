from django.contrib import admin
from .models import Genre, ContentItem, Favourite, UserProfile
from django.core.exceptions import ValidationError


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['username', 'name', 'phone', 'subscription_status', 'city', 'subscription_until']
    search_fields = ['username', 'name', 'phone', 'city']
    list_filter = ['subscription_status', 'city']
    ordering = ['-subscription_until']


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'content_item']
    search_fields = ['telegram_id', 'content_item__title']


@admin.register(ContentItem)
class ContentItemAdmin(admin.ModelAdmin):
    def get_fields(self, request, obj=None):
        fields = ['title', 'subtitle', 'genre', 'content_type', 'telegram_url', 'duration']
        if obj is None or obj.content_type == 'video':
            fields.append('thumbnail')
        return fields

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.content_type != 'video':
            return ['thumbnail']
        return []

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.content_type != 'video' and 'thumbnail' in form.base_fields:
            form.base_fields['thumbnail'].required = False
        return form

    list_display = ['title', 'genre', 'content_type']
    search_fields = ['title', 'subtitle']
    list_filter = ['genre', 'content_type']


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ['title']
    search_fields = ['title']
