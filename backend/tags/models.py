from django.db import models

from tags import constants


class Tag(models.Model):

    name = models.CharField(
        'Название тега',
        max_length=constants.MAX_LENGTH_TAG,
        unique=True,
        help_text=constants.HELP_TEXT_TAG,
    )
    slug = models.SlugField(
        'Слаг тега',
        max_length=constants.MAX_LENGTH_TAG,
        unique=True,
        help_text=constants.HELP_TEXT_SLUG,
    )

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'Теги'
        db_table = 'Tags'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'slug'],
                name='unique_tag'
            )
        ]

    def __str__(self):
        return self.name
