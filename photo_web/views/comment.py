import json
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from photo_web.services.comment_service import CommentService


class CreateCommentView(LoginRequiredMixin, View):
    def post(self, request):
        try: data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный формат JSON"}, status=400)

        photo_id = data.get('photo_id')
        text = data.get('text')
        parent_id = data.get('parent_id')

        if not photo_id or not text:
            return JsonResponse({"error": "Отсутствуют обязательные поля (photo_id, text)"}, status=400)

        try:
            result = CommentService.create_comment(request.user, int(photo_id), text, parent_id)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=400)
        except Exception:
            return JsonResponse({"error": "Внутренняя ошибка сервера"}, status=500)

        return JsonResponse({"status": "success", **result}, status=201)


class UpdateCommentView(LoginRequiredMixin, View):
    def post(self, request):
        try: data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный формат JSON"}, status=400)

        comment_id = data.get('comment_id')
        text = data.get('text')

        if not comment_id or not text:
            return JsonResponse({"error": "Отсутствуют обязательные поля (comment_id, text)"}, status=400)

        try:
            result = CommentService.update_comment(request.user, int(comment_id), text)
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=403)
        except Exception:
            return JsonResponse({"error": "Внутренняя ошибка сервера"}, status=500)

        return JsonResponse({"status": "success", **result}, status=200)


class DeleteCommentView(LoginRequiredMixin, View):
    def post(self, request):
        try: data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный формат JSON"}, status=400)

        comment_id = data.get('comment_id')
        if not comment_id:
            return JsonResponse({"error": "Отсутствует comment_id"}, status=400)

        try:
            result = CommentService.delete_comment(request.user, int(comment_id))
        except ValueError as e:
            return JsonResponse({"error": str(e)}, status=403)
        except Exception:
            return JsonResponse({"error": "Внутренняя ошибка сервера"}, status=500)

        return JsonResponse({"status": "success", **result}, status=200)