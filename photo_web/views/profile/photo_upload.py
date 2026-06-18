from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from photo_web.services.profile.photo_upload_service import PhotoUploadService


class PhotoUploadView(LoginRequiredMixin, View):
    def post(self, request):
        # inputs — данные для валидации формой
        inputs = {
            'title': request.POST.get('title', '').strip(),
            'description': request.POST.get('description', '').strip(),
        }
        
        # kwargs — дополнительные параметры (не валидируются формой)
        result = PhotoUploadService.execute(
            inputs=inputs,
            user=request.user,
            image_file=request.FILES.get('image')
        )
        
        return JsonResponse({"status": "success", **result}, status=201)