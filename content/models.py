from django.db import models
from .validators import validate_file_size
from django.core.exceptions import ValidationError


# 📌 Жанр (обычный или спец)
class Genre(models.Model):
    GENRE_KIND_CHOICES = [
        ("default", "Обычный жанр"),
        ("special", "Спецжанр (с группами)"),
    ]

    title = models.CharField(max_length=100)
    kind = models.CharField(
        max_length=20, choices=GENRE_KIND_CHOICES, default="default"
    )

    def __str__(self):
        return f"{self.title} [{self.kind}]"


# 📌 Группы внутри спецжанра
class Group(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name="groups")
    title = models.CharField(max_length=150)

    # ✅ Новые поля для страницы группы и админки
    description = models.TextField(blank=True, help_text="Краткое описание группы")
    expert = models.CharField(max_length=255, blank=True, help_text="Имя эксперта")
    cover = models.ImageField(
        upload_to="group_covers/",
        blank=True,
        null=True,
        validators=[validate_file_size],
        help_text="Обложка группы (до 2 МБ)",
    )

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"

    def __str__(self):
        return f"{self.title} (Group of {self.genre.title})"


# 📌 Контент (с привязкой либо к жанру, либо к группе)
class ContentItem(models.Model):
    CONTENT_TYPE_CHOICES = [
        ("video", "🎥 Видео"),
        ("audio", "🎧 Аудио"),
        ("file", "📄 Файл"),
    ]

    genre = models.ForeignKey(
        Genre, on_delete=models.CASCADE, related_name="items", null=True, blank=True
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, related_name="items", null=True, blank=True
    )

    title = models.CharField(max_length=200)
    subtitle = models.TextField(blank=True, null=True, help_text="Краткое описание")
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES)
    telegram_url = models.URLField(help_text="Ссылка на сообщение в Telegram")
    duration = models.CharField(max_length=20, help_text="Например: 00:00:45")
    thumbnail = models.ImageField(
        upload_to="thumbnails/",
        blank=True,
        null=True,
        validators=[validate_file_size],
        help_text="Только для видео. Макс. 2 МБ",
    )

    def __str__(self):
        return f"{self.title} ({self.content_type})"

    def clean(self):
        # Запрещаем указывать одновременно genre и group
        if self.genre and self.group:
            raise ValidationError(
                {"group": "Контент нельзя привязать сразу и к жанру, и к группе"}
            )

        # Проверка дубликата внутри жанра или группы
        qs = ContentItem.objects.filter(title__iexact=self.title)
        if self.genre:
            qs = qs.filter(genre=self.genre)
        if self.group:
            qs = qs.filter(group=self.group)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError(
                {"title": "В этом разделе уже есть блок с таким названием"}
            )


# 📌 Избранное
class Favourite(models.Model):
    telegram_id = models.CharField(max_length=20)
    content_item = models.ForeignKey(ContentItem, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("telegram_id", "content_item")

    def __str__(self):
        return f"{self.telegram_id} ♥ {self.content_item.title}"


# 📌 Профиль пользователя
class UserProfile(models.Model):
    username = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    subscription_status = models.BooleanField(default=False)
    city = models.CharField(max_length=100)
    subscription_until = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.name})"


# 📌 Новости (What's new)
class NewsItem(models.Model):
    title = models.CharField("Заголовок", max_length=200, blank=True)
    image = models.ImageField("Изображение", upload_to="news/")
    url = models.URLField("Ссылка", blank=True)
    is_active = models.BooleanField("Активно", default=True)
    order = models.PositiveIntegerField(
        "Порядок", default=0, help_text="Меньше — выше в списке"
    )
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Новость (What's new)"
        verbose_name_plural = "Новости (What's new)"

    def __str__(self):
        return self.title or f"News #{self.pk}"
