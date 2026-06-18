from django.db import transaction
from photo_web.models import Photo


class PhotoRestoreService:
    """
    Сервисный объект для восстановления фотографии, запланированной к удалению.
    """
    
    @classmethod
    @transaction.atomic
    def restore_photo(cls, user, photo_id: int) -> dict:
        """
        Отменяет удаление фотографии.
        
        Args:
            user: Авторизованный пользователь
            photo_id: ID фотографии
        """
        # Получаем фото
        photo = Photo.objects.get(id=photo_id)  # Photo.DoesNotExist → 404
        
        if photo.author != user:
            raise PermissionError("Вы можете восстанавливать только свои фотографии") 
        
        # Статус
        if photo.status != Photo.Status.scheduled_deletion:
            raise ValueError("Фотография не запланирована к удалению")
        
        # Восстанавливаем статус
        # Если фото было одобрено до планирования удаления — возвращаем в approved
        # Иначе — в moderated (на повторную модерацию)
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