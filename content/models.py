from django.db import models
from .validators import validate_file_size  # ✅ проверка на размер thumbnail
from django.core.exceptions import ValidationError


# 📌 Модель жанра
class Genre(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


# 📌 Модель контента
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

    def clean(self):
        # Проверка дубликата title внутри жанра (кейс insensitive!)
        qs = ContentItem.objects.filter(genre=self.genre, title__iexact=self.title)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({'title': "В данном направлении уже есть блок с таким названием"})



# 📌 Модель избранного (для Telegram пользователей)
class Favourite(models.Model):
    telegram_id = models.CharField(max_length=20)  # ID или username Telegram пользователя
    content_item = models.ForeignKey(ContentItem, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('telegram_id', 'content_item')

    def __str__(self):
        return f"{self.telegram_id} ♥ {self.content_item.title}"


# 📌 Пользовательская модель (UserProfile)
class UserProfile(models.Model):
    username = models.CharField(max_length=100)  # Telegram username или ID
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    subscription_status = models.BooleanField(default=False)
    city = models.CharField(max_length=100)
    subscription_until = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.name})"
