from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from foodgram.constants import MAX_NAME_LENGTH


class User(AbstractUser):
    avatar = models.ImageField(
        verbose_name='Аватар',
        upload_to='avatars',
        null=True,
    )
    email = models.EmailField('email', unique=True)
    first_name = models.CharField('имя', max_length=MAX_NAME_LENGTH)
    last_name = models.CharField('фамилия', max_length=MAX_NAME_LENGTH)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)
        if self.username.lower() == 'me':
            raise ValidationError('Username "me" недоступен')


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
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_user_author'
            ),
            models.CheckConstraint(
                check=~models.Q(user_id=models.F('author_id')),
                name='check_self_follow'
            )
        ]
