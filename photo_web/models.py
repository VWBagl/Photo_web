from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill, ResizeToFit



def user_avatar_path(instance, filename):
    # instance — это объект User, filename — исходное имя файла
    return f'avatars/user_{instance.id}/{filename}'

class User(AbstractUser):
    #Флаг - "Является ли пользователь модератором"
    is_moderator = models.BooleanField(default=False) #По умолчанию роль модератора не присвоена
    
    #Оригинал аватара хранимый в БД, как путь к файлу
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        null=True, blank=True,
        #Допустимые расширения файлов изображений в аватаре
        validators=[FileExtensionValidator(['jpg','jpeg','png','webp'])]
        )
    
    #Версии изображения - виртуальные поля модели, не являются полями БД
    #Версия аватара для отображения в комментариях / в шапке сайта
    avatar_small = ImageSpecField(
        source='avatar',
        processors=[ResizeToFill(50,50)],   #ResizeToFill - обрезает до указанных размеров (от центра)
        format='JPEG',
        options={'quality':80}
        )
    #Версия аватара для отображения в профиле
    avatar_profile = ImageSpecField(
        source='avatar',
        processors=[ResizeToFit(150,150)],  #ResizeToFit - масштабирует сохраняя пропорции
        format='JPEG',
        options={'quality':85}
        )
    
    def __str__(self):
        return self.username
    
def photo_original_path(instance, filename):
    return f'photos/user_{instance.author_id}/original/{filename}'

def photo_previous_path(instance, filename):
    return f'photos/user_{instance.author_id}/previous/{filename}'
    
class Photo(models.Model):

    class Status(models.TextChoices):
        moderated = 'moderated'
        approved = 'approved'
        rejected = 'rejected'
        scheduled_deletion = 'deletion_scheduled'
        deleted = 'deleted'

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='photos'
        )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.moderated)

    original_image = models.ImageField(upload_to=photo_original_path)
    previous_image = models.ImageField(upload_to=photo_previous_path, 
                                       null=True, blank=True)
    
    votes_count = models.PositiveIntegerField(default=0, editable=False)
    comments_count = models.PositiveIntegerField(default=0, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    scheduled_deletion_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} — {self.author.username}"

class Vote(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE, related_name='vites_given')
    photo = models.ForeignKey(Photo,on_delete=models.CASCADE, related_name='votes')
    
    class Meta:
        constraints = [models.UniqueConstraint(fields=['user','photo'], name='unique_user_photo_vote')]
    
    def __str__(self):
        return f"{self.user.username} → {self.photo.title}"
    
class Comment(models.Model):
    photo = models.ForeignKey(Photo, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='replies'
        )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Comment from {self.author} for {self.photo.title}'