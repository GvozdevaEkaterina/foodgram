from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    is_subscribed = models.BooleanField(default=False)
    avatar = models.ImageField(
        'Аватар',
        upload_to='avatars',
        null=True,
        default=None
    )
