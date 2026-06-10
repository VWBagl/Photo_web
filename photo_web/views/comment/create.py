import json
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from photo_web.services.comment.create_service import CommentCreateService


class CreateCommentView(LoginRequiredMixin, View):
    def post(self, request):
        # 1. Парсинг JSON
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный формат JSON"}, status=400)

        photo_id = data.get('photo_id')
        text = data.get('text')
        parent_id = data.get('parent_id')

        # 2. Вызов сервиса
        try:
            # Если photo_id=None, int(None) вызовет TypeError, который мы перехватим ниже
            result = CommentCreateService.create(
                user=request.user,
                photo_id=int(photo_id),
                text=text,
                parent_id=parent_id
            )
        except TypeError:
            # ИСПРАВЛЕНИЕ: Обязательно указываем status=400!
            return JsonResponse({'error': 'Отсутствуют обязательные поля'}, status=400)
        except ValueError as e:
            # ИСПРАВЛЕНИЕ: Возвращаем реальный текст ошибки из сервиса (пустой текст, длинный текст и т.д.)
            return JsonResponse({"error": str(e)}, status=400)
        except Exception:
            return JsonResponse({"error": "Внутренняя ошибка сервера"}, status=500)

        # 3. Успешный ответ
        return JsonResponse({"status": "success", **result}, status=201)