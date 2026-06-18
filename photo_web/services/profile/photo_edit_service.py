from django import forms
from service_objects.services import Service
from photo_web.models import Photo


class PhotoEditService(Service):
    """Для редактирования фотографии."""
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.photo_id = kwargs.pop('photo_id', None)
        self.image_file = kwargs.pop('image_file', None)
        super().__init__(*args, **kwargs)

    ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'webp']
    
    # Все поля опциональны
    title = forms.CharField(max_length=255, required=False)
    description = forms.CharField(max_length=5000, required=False)
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if title is not None:
            title = title.strip()
            if not title:
                raise forms.ValidationError("Название фотографии не может быть пустым")
        return title

    def process(self):
        user = self.user
        photo_id = self.photo_id
        image_file = self.image_file
        
        # Photo.DoesNotExist - 404
        photo = Photo.objects.get(id=photo_id)
        
        # PermissionError - 403
        if photo.author != user:
            raise PermissionError("Вы можете редактировать только свои фотографии")
        
        if photo.status in [Photo.Status.scheduled_deletion, Photo.Status.deleted]:
            raise PermissionError("Нельзя редактировать фотографию, которая удаляется или удалена")
        
        # Определяем, что изменилось
        title = self.cleaned_data.get('title')
        description = self.cleaned_data.get('description')
        
        title_changed = title is not None and title != photo.title
        description_changed = description is not None and description.strip() != (photo.description or '')
        file_changed = image_file is not None
        
        # Валидация файла
        if file_changed:
            file_extension = image_file.name.split('.')[-1].lower()
            if file_extension not in self.ALLOWED_EXTENSIONS:
                raise ValueError(
                    f"Недопустимый тип файла. Разрешены: {', '.join(self.ALLOWED_EXTENSIONS)}"
                )
        
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
        if file_changed:
            if photo.original_image:
                photo.previous_image = photo.original_image
            photo.original_image = image_file
            photo.status = Photo.Status.moderated
        
        if title_changed:
            photo.title = title
        if description_changed:
            photo.description = description.strip()
        
        photo.save()
        
        message = ('Фотография обновлена и отправлена на повторную модерацию' 
                   if file_changed else 'Фотография успешно обновлена')
        
        return {
            'id': photo.id,
            'title': photo.title,
            'description': photo.description,
            'status': photo.status,
            'image_url': photo.original_image.url,
            'updated_at': photo.updated_at.strftime('%d.%m.%Y %H:%M'),
            'message': message
        }