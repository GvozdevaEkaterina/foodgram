from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='avatars',
        null=True,
        default=None
    )
    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'


User = get_user_model()


class Subscriptions(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers'
    )

    class Meta:
        unique_together = ('user', 'author', )
