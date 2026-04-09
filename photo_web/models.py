from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit


def user_avatar_path(instance, filename):
    # instance — это объект User, filename — исходное имя файла
    return f'avatars/user_{instance.id}/{filename}'

class User(AbstractUser):
    #Флаг - "Является ли пользователь модератором"
    is_moderator = models.BooleanField(
        #По умолчанию роль модератора не присвоена
        default=False
        )
    
    #Оригинал аватара хранимый в БД, как путь к файлу
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        null=True,
        blank=True,
        #Допустимые расширения файлов изображений в аватаре
        validators=[FileExtensionValidator(['jpg','jpeg','png','webp'])]
        )
    
    #Версии изображения - виртуальные поля модели, не являются полями БД
    #Версия аватара для отображения в комментариях / в шапке сайта
    avatar_small = ImageSpecField(
        source='avatar',
        #ResizeToFill - обрезает до указанных размеров (от центра)
        processors=[ResizeToFill(50,50)],
        format='JPEG',
        options={'quality':80}
        )
    #Версия аватара для отображения в профиле
    avatar_profile = ImageSpecField(
        source='avatar',
        #ResizeToFit - масштабирует сохраняя пропорции
        processors=[ResizeToFit(150,150)],
        format='JPEG',
        options={'quality':85}
    )