from django.db import models
from django.contrib.auth.models import AbstractUser


class MyUsers(AbstractUser):
    '''Модель пользователя'''
    USERNAME = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    email = models.EmailField(
        'email_adress',
        max_length=256,
        unique=False,
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    '''Модель подписчика'''
    user = models.ForeignKey(
        MyUsers, on_delete=models.CASCADE, related_name='follower',
    )
    following = models.ForeignKey(
        MyUsers, on_delete=models.CASCADE, related_name='following',
    )

    def __str__(self):
        return f'{self.user.username}, {self.following.username}'

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
