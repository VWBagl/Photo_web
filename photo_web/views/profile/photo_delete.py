from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from photo_web.services.profile.photo_delete_service import PhotoDeleteService


class PhotoDeleteView(LoginRequiredMixin, View):
    """
    Вьюха для отложенного удаления фотографии.
    """
    
    def delete(self, request, photo_id):
        # Вызываем сервис
        result = PhotoDeleteService.schedule_deletion(
            user=request.user,
            photo_id=int(photo_id)
        )
        
        return JsonResponse({"status": "success", **result}, status=200)