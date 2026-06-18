from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist


class ServiceErrorMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        return self.get_response(request)
    
    def process_exception(self, request, exception):
        # Только для API-запросов
        if not request.content_type:
            return None
        
        is_api = 'application/json' in request.content_type or 'multipart/form-data' in request.content_type
        if not is_api:
            return None
        
        # ObjectDoesNotExist  - 404 Not Found
        if isinstance(exception, ObjectDoesNotExist):
            return JsonResponse({"error": str(exception) or "Объект не найден"}, status=404)
        
        # PermissionError  - 403 Forbidden
        if isinstance(exception, PermissionError):
            return JsonResponse({"error": str(exception)}, status=403)
        
        # ValueError  - 400 Bad Request
        if isinstance(exception, ValueError):
            return JsonResponse({"error": str(exception)}, status=400)
        
        # Всё остальное  - 500 Internal Server Error
        return JsonResponse({"error": "Внутренняя ошибка сервера"}, status=500)