from django.db import models
from django.contrib.auth.models import AbstractUser


class MyUsers(AbstractUser):
    '''Модель пользователя'''
    username = models.CharField(
        verbose_name="Имя пользователя",
        max_length=255,
        unique=True,
    )
    email = models.EmailField(
        verbose_name="Элетронная почта",
        max_length=255,
        unique=True,
    )
    first_name = models.CharField("Имя", max_length=255, blank=True)
    last_name = models.CharField("Фамилия", max_length=255, blank=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ("id",)

    def __str__(self):
        return self.username


class Follow(models.Model):
    '''Модель подписчика'''
    user = models.ForeignKey(
        MyUsers,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    following = models.ForeignKey(
        MyUsers,
        on_delete=models.CASCADE,
        related_name='following',
    )

    def __str__(self):
        return f'{self.user.username}, {self.following.username}'

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        ordering = ("-id",)
