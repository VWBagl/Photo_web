from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from photo_web.services.profile.photo_upload_service import PhotoUploadService


class PhotoUploadView(LoginRequiredMixin, View):
    """
    Вьюха для загрузки фотографии.
    """
    
    def post(self, request):
        # Извлекаем данные из запроса
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        image_file = request.FILES.get('image')
        
        # Вызываем сервис
        result = PhotoUploadService.upload_photo(
            user=request.user,
            title=title,
            description=description,
            image_file=image_file
        )

        return JsonResponse({"status": "success", **result}, status=201)