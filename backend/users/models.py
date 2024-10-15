# from django.contrib.auth.models import AbstractUser
# from django.db import models

# from users import constants


# class User(AbstractUser):

#     username = models.CharField(
#         'Имя пользователя',
#         max_length=constants.MAX_LENGTH_NAME,
#         unique=True,
#     )
#     email = models.EmailField(
#         'email',
#         max_length=constants.MAX_LENGTH_EMAIL,
#         unique=True,
#     )
#     first_name = models.CharField(
#         'Имя',
#         max_length=constants.MAX_LENGTH_NAME,
#     )
#     last_name = models.CharField(
#         'Фамилия',
#         max_length=constants.MAX_LENGTH_NAME,
#     )
#     password = models.CharField(
#         'Пароль',
#         max_length=constants.MAX_LENGTH_PASSWORD,
#     )

#     class Meta:
#         verbose_name = 'Пользователь'
#         verbose_name_plural = 'Пользователи'
#         ordering = ('username',)

#     def __str__(self):
#         return self.username
