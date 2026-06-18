from django.db import transaction
from photo_web.models import Photo


class PhotoEditService:
    """
    - Если меняется только текст (title/description) — статус не меняется
    - Если меняется файл — текущий original_image копируется в previous_image,
      новый файл становится original_image, статус сбрасывается в moderated
    """
    
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']
    
    @classmethod
    @transaction.atomic
    def edit_photo(cls, user, photo_id: int, title: str = None, 
                   description: str = None, image_file=None) -> dict:
        """
        Редактирует фотографию от имени пользователя.
        
        Args:
            user: Авторизованный пользователь
            photo_id: ID фотографии
            title: Новое название (опционально)
            description: Новое описание (опционально)
            image_file: Новый файл изображения (опционально)
        """
        # Получаем фото
        photo = Photo.objects.get(id=photo_id)  # Photo.DoesNotExist - 404

        if photo.author != user:
            raise PermissionError("Вы можете редактировать только свои фотографии")
        
        # Проверяем статус
        if photo.status in [Photo.Status.scheduled_deletion, Photo.Status.deleted]:
            raise ValueError("Нельзя редактировать фотографию, которая удаляется или удалена")

        # Валидация входных данных
        title_changed = False
        description_changed = False
        file_changed = False
        
        # Проверяем title
        if title is not None:
            title = title.strip()
            if not title:
                raise ValueError("Название фотографии не может быть пустым")
            if len(title) > 255:
                raise ValueError("Название слишком длинное (макс. 255 символов)")
            if title != photo.title:
                title_changed = True
        
        # Проверяем description
        if description is not None:
            description = description.strip()
            if len(description) > 5000:
                raise ValueError("Описание слишком длинное (макс. 5000 символов)")
            if description != photo.description:
                description_changed = True
        
        # Проверяем файл
        if image_file is not None:
            file_extension = image_file.name.split('.')[-1].lower()
            if file_extension not in cls.ALLOWED_EXTENSIONS:
                raise ValueError(f"Недопустимый тип файла. Разрешены: {', '.join(cls.ALLOWED_EXTENSIONS)}")
            file_changed = True
        
        # Если ничего не изменилось — возвращаем текущие данные
        if not (title_changed or description_changed or file_changed):
            return {
                'id': photo.id,
                'title': photo.title,
                'description': photo.description,
                'status': photo.status,
                'image_url': photo.original_image.url,
                'updated_at': photo.updated_at.strftime('%d.%m.%Y %H:%M'),
                'message': 'Изменений не было'
            }
        
        # Применяем изменения
        # Если меняется файл — сохраняем текущий в previous_image
        if file_changed:
            # Копируем текущий original_image в previous_image
            if photo.original_image:
                photo.previous_image = photo.original_image
            
            # Устанавливаем новый файл
            photo.original_image = image_file
            
            # Сбрасываем статус на moderated (повторная модерация)
            photo.status = Photo.Status.moderated
        
        # Обновляем текстовые поля
        if title_changed:
            photo.title = title
        
        if description_changed:
            photo.description = description
        
        # Сохраняем изменения
        photo.save()
        
        # Формируем сообщение
        if file_changed:
            message = 'Фотография обновлена и отправлена на повторную модерацию'
        else:
            message = 'Фотография успешно обновлена'

        return {
            'id': photo.id,
            'title': photo.title,
            'description': photo.description,
            'status': photo.status,
            'image_url': photo.original_image.url,
            'updated_at': photo.updated_at.strftime('%d.%m.%Y %H:%M'),
            'message': message
        }