from django.shortcuts import render
from ..services.gallery_service import GalleryService

def _prepare_gallery_context(request):
    # извлекает параметры из запроса, 
    # вызывает сервис и формирует контекст для шаблона.
    sort_by = request.GET.get('sort', 'date')
    search = request.GET.get('q', '')
    page = request.GET.get('p', 1)

    photos = GalleryService.get_gallery_page(
        sort_by=sort_by,
        search_query=search,
        page_number=page
    )
    
    return {
    # Контекст шаблона
        'photos': photos, # для {% for photo in photos %}
        'search_query': search, # для сохранения текста поиска после отправки формы
        'current_sort': sort_by, # для сохранения сортировки между ссылками пагинации
        
        # Передача готовых флагов, вместо строк
        'is_sort_date': sort_by == 'date',
        'is_sort_votes': sort_by == 'votes',
        'is_sort_comments': sort_by == 'comments',
    }

def gallery_view(request):
    # Полная страница галереи (первый заход, перезагрузка
    context = _prepare_gallery_context(request)
    return render(request, 'photo_web/photo_gallery.html', context)

def gallery_fragment_view(request):
    # Фрагмент сетки для асинхронной подгрузки
    context = _prepare_gallery_context(request)
    return render(request, 'photo_web/_photo_grid.html', context)