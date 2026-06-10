import json
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from photo_web.services.comment.update_delete_service import CommentManageService


class CommentManageView(LoginRequiredMixin, View):
    
    def _execute_service_action(self, service_method, **kwargs):
        try:
            result = service_method(**kwargs)
        except (ValueError, TypeError) as e:
            return JsonResponse({"error": str(e)}, status=403)
        except Exception:
            return JsonResponse({"error": "Внутренняя ошибка сервера"}, status=500)
        
        return JsonResponse({"status": "success", **result}, status=200)

    def patch(self, request, comment_id):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный формат JSON"}, status=400)

        text = data.get('text')

        return self._execute_service_action(
            service_method=CommentManageService.update,
            user=request.user,
            comment_id=int(comment_id),
            text=text
        )

    def delete(self, request, comment_id):
        return self._execute_service_action(
            service_method=CommentManageService.delete,
            user=request.user,
            comment_id=int(comment_id)
        )