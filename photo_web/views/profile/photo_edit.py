import json
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from photo_web.services.profile.photo_edit_service import PhotoEditService


def _parse_edit_request(request):
    """Данные из request для редактирования фото."""
    content_type = request.content_type
    
    if 'multipart/form-data' in content_type:
        return {
            'title': request.POST.get('title'),
            'description': request.POST.get('description'),
            'image_file': request.FILES.get('image')
        }
    elif 'application/json' in content_type:
        data = json.loads(request.body)
        return {
            'title': data.get('title'),
            'description': data.get('description'),
            'image_file': None
        }
    else:
        raise ValueError("Неподдерживаемый тип контента")


class PhotoEditView(LoginRequiredMixin, View):
    def patch(self, request, photo_id):
        data = _parse_edit_request(request)
        
        # Данные на inputs (для валидации) и kwargs
        inputs = {
            'title': data['title'],
            'description': data['description'],
        }
        
        result = PhotoEditService.execute(
            inputs=inputs,
            user=request.user,
            photo_id=int(photo_id),
            image_file=data['image_file']
        )
        
        return JsonResponse({"status": "success", **result}, status=200)