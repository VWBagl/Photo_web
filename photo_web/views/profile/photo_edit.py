import json
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from photo_web.services.profile.photo_edit_service import PhotoEditService


def _parse_edit_request(request):
    """Парсит данные из request для редактирования фото."""
    content_type = request.content_type
    
    if 'multipart/form-data' in content_type:
        return (
            request.POST.get('title'),
            request.POST.get('description'),
            request.FILES.get('image')
        )
    elif 'application/json' in content_type:
        data = json.loads(request.body)
        return (
            data.get('title'),
            data.get('description'),
            None
        )
    else:
        raise ValueError("Неподдерживаемый тип контента")


class PhotoEditView(LoginRequiredMixin, View):
    def patch(self, request, photo_id):
        title, description, image_file = _parse_edit_request(request)
        
        result = PhotoEditService.edit_photo(
            user=request.user,
            photo_id=int(photo_id),
            title=title,
            description=description,
            image_file=image_file
        )
        
        return JsonResponse({"status": "success", **result}, status=200)