from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from photo_web.services.profile.photo_restore_service import PhotoRestoreService


class PhotoRestoreView(LoginRequiredMixin, View):
    def post(self, request, photo_id):
        result = PhotoRestoreService.execute(
            inputs={},
            user=request.user,
            photo_id=int(photo_id)
        )
        return JsonResponse({"status": "success", **result}, status=200)