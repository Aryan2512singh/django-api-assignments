

from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class EmailVerification(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verification",
    )
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    attempts = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return self.user.email
