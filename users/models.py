from django.db import models
from content.models import ContentItem


class User(models.Model):
    telegram_id = models.CharField(max_length=32, unique=True)
    full_name = models.CharField(max_length=255)
    city = models.CharField(max_length=100, blank=True)
    is_resident = models.BooleanField(default=False)
    subscription_until = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.full_name or f"User {self.telegram_id}"


class Favourite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favourites')
    content = models.ForeignKey(ContentItem, on_delete=models.CASCADE, related_name='user_favourites')  # <--- вот тут ключевое

    class Meta:
        unique_together = ('user', 'content')
