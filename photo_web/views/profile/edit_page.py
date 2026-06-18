from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from photo_web.services.profile.page_photo_edit_service import PagePhotoEditService


class PhotoEditPageView(LoginRequiredMixin, View):
    """
    Вьюха для отображения страницы редактирования фотографии.
    """
    
    def get(self, request, photo_id):
        # Получаем фото с проверкой прав и статуса
        photo = PagePhotoEditService.get_photo_for_edit(
            user=request.user,
            photo_id=int(photo_id)
        )
        
        return render(request, 'photo_web/edit.html', {'photo': photo})