from django.db import models
from django.conf import settings


class Vote(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE, 
        related_name='vites_given'
    )
    photo = models.ForeignKey(
        'Photo', 
        on_delete=models.CASCADE,
        related_name='votes')
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'photo'], 
                name='unique_user_photo_vote')
        ]
    
    def __str__(self):
        return f"{self.user.username} → {self.photo.title}"