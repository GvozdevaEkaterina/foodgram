from django.db import models

from foodgram.constants import MAX_TAG_NAME, MAX_TAG_SLUG_NAME


class Tag(models.Model):
    name = models.CharField(max_length=MAX_TAG_NAME, unique=True)
    slug = models.SlugField(max_length=MAX_TAG_SLUG_NAME, unique=True)

    def __str__(self):
        return self.name