from django.db import models

class UserProfile(models.Model):
    username = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    subscription_status = models.BooleanField(default=False)
    city = models.CharField(max_length=100)
    subscription_until = models.DateField(null=True, blank=True)
    telegram_id = models.CharField(max_length=64, null=True, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    def avatar_url(self):
        return self.avatar.url if self.avatar else None

    def __str__(self):
        return f"{self.username} ({self.name})"
