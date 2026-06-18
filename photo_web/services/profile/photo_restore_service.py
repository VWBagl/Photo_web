from service_objects.services import Service
from photo_web.models import Photo


class PhotoRestoreService(Service):
    """Сервис восстановления фотографии, запланированной к удалению."""
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.photo_id = kwargs.pop('photo_id', None)
        super().__init__(*args, **kwargs)
    
    def process(self):
        user = self.user
        photo_id = self.photo_id
        
        # Photo.DoesNotExist - 404
        photo = Photo.objects.get(id=photo_id)
        
        if photo.author != user:
            raise PermissionError("Вы можете восстанавливать только свои фотографии")
        
        if photo.status != Photo.Status.scheduled_deletion:
            raise ValueError("Фотография не запланирована к удалению")
        
        # Восстанавливаем статус
        if photo.approved_at:
            photo.status = Photo.Status.approved
        else:
            photo.status = Photo.Status.moderated
        
        photo.scheduled_deletion_at = None
        photo.save()
        
        return {
            'id': photo.id,
            'status': photo.status,
            'message': 'Удаление отменено, фотография восстановлена'
        }