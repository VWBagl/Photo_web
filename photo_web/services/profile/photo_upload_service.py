from django import forms
from service_objects.services import Service
from photo_web.models import Photo


class PhotoUploadService(Service):
    """Сервисный объект для загрузки фотографии пользователем."""
    
    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']
    
    # Поля для валидации
    title = forms.CharField(max_length=255)
    description = forms.CharField(required=False, max_length=5000)
    
    def __init__(self, *args, **kwargs):
        # Извлекаем user и image_file из kwargs до вызова super().__init__
        self.user = kwargs.pop('user', None)
        self.image_file = kwargs.pop('image_file', None)
        super().__init__(*args, **kwargs)
    
    def clean_title(self):
        """Кастомная валидация названия."""
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError("Название фотографии обязательно")
        return title
    
    def process(self):
        """Бизнес-логика: создание объекта Photo."""
        user = self.user
        image_file = self.image_file
        
        # Валидация файла
        if not image_file:
            raise ValueError("Файл изображения обязателен")
        
        file_extension = image_file.name.split('.')[-1].lower()
        if file_extension not in self.ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Недопустимый тип файла. Разрешены: {', '.join(self.ALLOWED_EXTENSIONS)}"
            )
        
        photo = Photo.objects.create(
            author=user,
            title=self.cleaned_data['title'],
            description=self.cleaned_data.get('description', '').strip(),
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