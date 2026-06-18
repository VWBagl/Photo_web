from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from photo_web.services.profile.photo_list_service import PhotoListService


class MyPhotosView(LoginRequiredMixin, View):
    """
    Вьюха для отображения списка фотографий пользователя с фильтрацией.
    """
    
    def get(self, request):
        # Извлекаем параметры из запроса
        status_filter = request.GET.get('status')
        page = request.GET.get('page', 1)
        
        # Вызываем сервис
        context = PhotoListService.get_user_photos(
            user=request.user,
            status_filter=status_filter,
            page_number=int(page)
        )
        
        return render(request, 'photo_web/my_photos.html', context)