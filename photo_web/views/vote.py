import json
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse

from photo_web.services.vote_service import VoteService


class SwitchVoteView(LoginRequiredMixin, View):

    def post(self, request):
        # Парсинг тела запроса
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Некорректный формат JSON"}, status=400)

        photo_id = data.get("photo_id")

        # Валидация входных параметров
        if not photo_id or not isinstance(photo_id, int):
            return JsonResponse({"error": "Требуется корректный photo_id (целое число)"}, status=400)
        
        if photo_id <= 0:
            return JsonResponse({"error": "photo_id должен быть положительным"}, status=400)

        # Вызов сервиса
        try:
            result = VoteService.switch_vote(user=request.user, photo_id=photo_id)
        except ValueError as e:
            # фото не найдено / не одобрено...
            return JsonResponse({"error": str(e)}, status=400)
        except Exception as e:
            return JsonResponse({"error": "Внутренняя ошибка сервера"}, status=500)

        # Формирование успешного ответа
        return JsonResponse({
            "status": "success",
            "action": result["action"],
            "votes_count": result["votes_count"]
            }, status=200)