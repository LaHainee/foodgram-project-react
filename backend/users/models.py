from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        blank=False
    )
    username = models.CharField(
        unique=True, blank=False,
        max_length=20
    )

    REQUIRED_FIELDS = ['username']
    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ('username',)

    def __str__(self):
        return self.email
