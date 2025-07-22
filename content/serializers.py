from rest_framework import serializers
from .models import ContentItem, Genre, Favourite


class ContentItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentItem
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):
    items = ContentItemSerializer(many=True)

    class Meta:
        model = Genre
        fields = ['id', 'title', 'items']


class FavouriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favourite
        fields = ['id', 'telegram_id', 'content_item', 'created_at']

