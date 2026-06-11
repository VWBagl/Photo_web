from photo_web.models import Photo
from django.db.models import Q
from django.core.paginator import Paginator

class GalleryService:
    @staticmethod
    # Возвращает страницу одобренных фотографий с применением поиска и сортировки
    def get_gallery_page(sort_by: str = 'date',
                         search_query: str = '',
                         page_number: int=1,
                         per_page: int=12):
        
        # Фильтр по одобренным фотографиям + подгрузка автора
        qs = Photo.objects.filter(status = Photo.Status.approved).select_related('author')

        # Поиск по подстроке author/title/description
        if search_query:
            qs = qs.filter(
                
                Q(author__username__icontains=search_query) |
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            ) # icontains - регистронезависимость
        
        sort_mapping = {
            'votes': '-votes_count',
            'comments': '-comments_count',
            'date': '-approved_at'
        } # "-" - по убыванию

        order_by = sort_mapping.get(sort_by, '-approved_at')
        # .get(key, default), если key - неизвестный, то будет default
        qs = qs.order_by(order_by)

        paginator = Paginator(qs,per_page)
        return paginator.get_page(page_number)