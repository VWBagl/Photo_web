from django.db import transaction
from photo_web.models import Photo


class PhotoUploadService:
    """
    Сервисный объект для загрузки фотографии пользователем.
    Отвечает за бизнес-логику: валидацию, создание объекта Photo, установку статуса.
    """
    
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']
    
    @classmethod
    @transaction.atomic
    def upload_photo(cls, user, title: str, description: str, image_file) -> dict:
        """
        Загружает фотографию от имени пользователя.
        
        Args:
            user: Авторизованный пользователь (owner)
            title: Название фотографии (обязательное)
            description: Описание фотографии (может быть пустым)
            image_file: Файл изображения (обязательное)
        """
        # Валидация входных данных
        if not title or not title.strip():
            raise ValueError("Название фотографии обязательно")
        
        if len(title) > 255:
            raise ValueError("Название слишком длинное (макс. 255 символов)")
        
        description = (description or "").strip()
        if len(description) > 5000:
            raise ValueError("Описание слишком длинное (макс. 5000 символов)")
        
        if not image_file:
            raise ValueError("Файл изображения обязателен")
        
        # Проверка расширения файла
        file_extension = image_file.name.split('.')[-1].lower()
        if file_extension not in cls.ALLOWED_EXTENSIONS:
            raise ValueError(f"Недопустимый тип файла. Разрешены: {', '.join(cls.ALLOWED_EXTENSIONS)}")
        
        # Создание объекта Photo
        photo = Photo.objects.create(
            author=user,
            title=title.strip(),
            description=description,
            original_image=image_file,
            status=Photo.Status.moderated
        )
        
        return {
            'id': photo.id,
            'title': photo.title,
            'description': photo.description,
            'status': photo.status,
            'image_url': photo.original_image.url,
            'created_at': photo.created_at.strftime('%d.%m.%Y %H:%M'),
            'message': 'Фотография успешно загружена и отправлена на модерацию'
        }