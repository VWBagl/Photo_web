from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from photo_web.services.profile.photo_delete_service import PhotoDeleteService


class PhotoDeleteView(LoginRequiredMixin, View):
    def delete(self, request, photo_id):
        result = PhotoDeleteService.execute(
            inputs={},  # Нет данных для валидации
            user=request.user,
            photo_id=int(photo_id)
        )
        return JsonResponse({"status": "success", **result}, status=200)