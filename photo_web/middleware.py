from django.http import JsonResponse
from django.core.exceptions import ObjectDoesNotExist
from service_objects.errors import InvalidInputsError


class ServiceErrorMiddleware:
    """
    Middleware для автоматической обработки исключений из сервисных объектов.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        return self.get_response(request)
    
    def process_exception(self, request, exception):
        # Только для API-запросов
        if not request.content_type:
            return None
        
        is_api = ('application/json' in request.content_type or 
                  'multipart/form-data' in request.content_type)
        if not is_api:
            return None
        
        # ObjectDoesNotExist - 404
        if isinstance(exception, ObjectDoesNotExist):
            return JsonResponse({"error": str(exception) or "Объект не найден"}, status=404)
        
        # PermissionError - 403
        if isinstance(exception, PermissionError):
            return JsonResponse({"error": str(exception)}, status=403)
        
        # InvalidInputsError (из django-service-objects) - 400
        if isinstance(exception, InvalidInputsError):
            # .errors — dict с ошибками по полям
            # .non_form_errors — список общих ошибок
            error_data = {
                "error": "Ошибка валидации",
                "field_errors": exception.errors,
            }
            if exception.non_form_errors:
                error_data["non_field_errors"] = exception.non_form_errors
            return JsonResponse(error_data, status=400)
        
        # ValueError - 400
        if isinstance(exception, ValueError):
            return JsonResponse({"error": str(exception)}, status=400)
        
        # Всё остальное - 500
        return JsonResponse({"error": "Внутренняя ошибка сервера"}, status=500)