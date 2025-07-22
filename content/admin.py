from django.contrib import admin
from .models import Genre, ContentItem
from .models import Favourite


@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'content_item']


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


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass
