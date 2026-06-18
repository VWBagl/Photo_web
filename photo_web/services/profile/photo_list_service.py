from django.core.paginator import Paginator
from photo_web.models import Photo


class PhotoListService:
    """
    Сервисный объект для получения списка фотографий пользователя с фильтрацией.
    """
    
    # Строковые параметры из url в статусы
    STATUS_MAPPING = {
        'moderated': Photo.Status.moderated,
        'approved': Photo.Status.approved,
        'rejected': Photo.Status.rejected,
        'scheduled_deletion': Photo.Status.scheduled_deletion,  # 'deletion_scheduled' в БД
    }
    
    @classmethod
    def get_user_photos(cls, user, status_filter: str = None, page_number: int = 1, per_page: int = 12) -> dict:
        """
        Возвращает страницу фотографий пользователя с применением фильтрации по статусу.
        """
        # только фото пользователя, исключая удалённые
        qs = Photo.objects.filter(author=user).exclude(status=Photo.Status.deleted)
        
        # Применяем фильтр по статусу, если указан
        if status_filter and status_filter in cls.STATUS_MAPPING:
            real_status = cls.STATUS_MAPPING[status_filter]
            qs = qs.filter(status=real_status)
        
        # Сортировка: новые сверху
        qs = qs.order_by('-created_at')
        
        # Пагинация
        paginator = Paginator(qs, per_page)
        page = paginator.get_page(page_number)
        
        # Подсчёт количества фото по статусам для фильтров
        base_qs = Photo.objects.filter(author=user).exclude(status=Photo.Status.deleted)
        counts = {
            'all': base_qs.count(),
            'moderated': base_qs.filter(status=Photo.Status.moderated).count(),
            'approved': base_qs.filter(status=Photo.Status.approved).count(),
            'rejected': base_qs.filter(status=Photo.Status.rejected).count(),
            'scheduled_deletion': base_qs.filter(status=Photo.Status.scheduled_deletion).count(),
        }
        
        return {
            'photos': page,
            'counts': counts,
            'current_filter': status_filter or 'all',
            'is_moderated': status_filter == 'moderated',
            'is_approved': status_filter == 'approved',
            'is_rejected': status_filter == 'rejected',
            'is_scheduled_deletion': status_filter == 'scheduled_deletion',
            'is_all': not status_filter or status_filter == 'all'
        }