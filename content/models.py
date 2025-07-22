from django.db import models
from .validators import validate_file_size
from django.contrib.auth.models import User
from django.db import models


class Favourite(models.Model):
    telegram_id = models.CharField(max_length=20)  # ID пользователя из Telegram
    content_item = models.ForeignKey('ContentItem', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('telegram_id', 'content_item')

    def __str__(self):
        return f"{self.telegram_id} ♥ {self.content_item.title}"





class Genre(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class ContentItem(models.Model):
    GENRE_TYPE_CHOICES = [
        ('video', '🎥 Видео'),
        ('audio', '🎧 Аудио'),
        ('file', '📄 Файл'),
    ]

    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True, null=True, help_text="Краткое описание контента")
    content_type = models.CharField(max_length=10, choices=GENRE_TYPE_CHOICES)
    telegram_url = models.URLField(help_text="Ссылка на сообщение в Telegram")

    duration = models.CharField(max_length=20, help_text="Например: 00:00:45")

    thumbnail = models.ImageField(
        upload_to='thumbnails/',
        blank=True,
        null=True,
        validators=[validate_file_size],
        help_text="Только для видео. Макс. 2 МБ"
    )

    def __str__(self):
        return f"{self.title} ({self.content_type})"

