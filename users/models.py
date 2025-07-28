from django.db import models

class UserProfile(models.Model):
    username = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    subscription_status = models.BooleanField(default=False)
    city = models.CharField(max_length=100)
    subscription_until = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.username} ({self.name})"
