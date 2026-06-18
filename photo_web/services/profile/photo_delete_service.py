from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from photo_web.models import Photo


class PhotoDeleteService:
    """
    Сервис отложенного удаления фотографии.
    Устанавливает статус scheduled_deletion и время удаления.
    """
    
    # Для теста: 1 минута. В боевом режиме: timedelta(days=1)
# После теста вернуть в 1
    DELETION_DELAY_MINUTES = 10/60
    
    @classmethod
    @transaction.atomic
    def schedule_deletion(cls, user, photo_id: int, delay_seconds: int = None) -> dict:
        """
        Планирует удаление фотографии через DELETION_DELAY_MINUTES.
        """
        # Получаем фото
        photo = Photo.objects.get(id=photo_id)  # Photo.DoesNotExist - 404

        if photo.author != user:
            raise PermissionError("Вы можете удалять только свои фотографии") 
        
        # Проверяем статус
        if photo.status == Photo.Status.scheduled_deletion:
            raise ValueError("Фотография уже запланирована к удалению")
        
        if photo.status == Photo.Status.deleted:
            raise ValueError("Фотография уже удалена")
        
        # Устанавливаем статус и время удаления
        if delay_seconds is not None:
            deletion_time = timezone.now() + timedelta(seconds=delay_seconds)
            message = f'Фотография будет удалена через {delay_seconds} сек. Вы можете отменить удаление.'
        else:
            deletion_time = timezone.now() + timedelta(minutes=cls.DELETION_DELAY_MINUTES)
            message = f'Фотография будет удалена через {cls.DELETION_DELAY_MINUTES} мин. Вы можете отменить удаление.'
        
        photo.status = Photo.Status.scheduled_deletion
        photo.scheduled_deletion_at = deletion_time
        photo.save()

        return {
            'id': photo.id,
            'status': photo.status,
            'scheduled_deletion_at': deletion_time.strftime('%d.%m.%Y %H:%M:%S'),
            'message': message
        }