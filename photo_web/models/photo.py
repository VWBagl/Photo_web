from django.db import models
from django.conf import settings


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
    description = models.TextField(
        blank=True, default='')

    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.moderated
    )

    original_image = models.ImageField(upload_to=photo_original_path)
    previous_image = models.ImageField(upload_to=photo_previous_path, 
        null=True, blank=True
    )
    
    votes_count = models.PositiveIntegerField(default=0, editable=False)
    comments_count = models.PositiveIntegerField(default=0, editable=False)

    created_at = models.DateTimeField(
        auto_now_add=True)
    approved_at = models.DateTimeField(
        null=True, blank=True)
    updated_at = models.DateTimeField(
        auto_now=True)
    scheduled_deletion_at = models.DateTimeField(
        null=True, blank=True)

    def __str__(self):
        return f"{self.title} — {self.author.username}"