from django.shortcuts import get_object_or_404
from photo_web.models import Photo


class PagePhotoEditService:
    """
    Сервисный объект для получения фотографии для редактирования.
    Проверяет права доступа и статус фотографии.
    """
    
    @classmethod
    def get_photo_for_edit(cls, user, photo_id: int):
        """
        Получает фотографию для редактирования с проверкой прав и статуса.
        
        Args:
            user: Авторизованный пользователь
            photo_id: ID фотографии
            
        Returns:
            Photo object
            
        Raises:
            Photo.DoesNotExist: Если фото не найдено (middleware вернёт 404)
            PermissionError: Если нет прав или статус не позволяет редактировать
        """
        # Получаем фото (если не найдено — Photo.DoesNotExist → 404)
        photo = get_object_or_404(Photo, id=photo_id)
        
        # Проверяем права доступа
        if photo.author != user:
            raise PermissionError("Вы можете редактировать только свои фотографии")
        
        # Проверяем статус
        if photo.status in [Photo.Status.scheduled_deletion, Photo.Status.deleted]:
            raise PermissionError("Нельзя редактировать фотографию, которая удаляется или удалена")
        
        return photo