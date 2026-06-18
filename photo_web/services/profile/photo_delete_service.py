from django.utils import timezone
from datetime import timedelta
from service_objects.services import Service
from photo_web.models import Photo


class PhotoDeleteService(Service):
    """Сервисный объект для отложенного удаления фотографии."""
    
    # Для теста: 10 секунд. Потом timedelta(days=1)
    DELETION_DELAY_MINUTES = 10/60

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.photo_id = kwargs.pop('photo_id', None)
        self.delay_seconds = kwargs.pop('delay_seconds', None)
        super().__init__(*args, **kwargs)        
    
    def process(self):
        user = self.user
        photo_id = self.photo_id
        delay_seconds = self.delay_seconds 
        
        # Photo.DoesNotExist - 404
        photo = Photo.objects.get(id=photo_id)
        
        # PermissionError - 403
        if photo.author != user:
            raise PermissionError("Вы можете удалять только свои фотографии")
        
        if photo.status == Photo.Status.scheduled_deletion:
            raise ValueError("Фотография уже запланирована к удалению")
        
        if photo.status == Photo.Status.deleted:
            raise ValueError("Фотография уже удалена")
        
        # Устанавливаем статус и время удаления
        if delay_seconds is not None:
            deletion_time = timezone.now() + timedelta(seconds=delay_seconds)
            message = f'Фотография будет удалена через {delay_seconds} сек. Вы можете отменить удаление.'
        else:
            deletion_time = timezone.now() + timedelta(minutes=self.DELETION_DELAY_MINUTES)
            message = f'Фотография будет удалена через {self.DELETION_DELAY_MINUTES} мин. Вы можете отменить удаление.'
        
        photo.status = Photo.Status.scheduled_deletion
        photo.scheduled_deletion_at = deletion_time
        photo.save()
        
        return {
            'id': photo.id,
            'status': photo.status,
            'scheduled_deletion_at': deletion_time.strftime('%d.%m.%Y %H:%M:%S'),
            'message': message
        }