from django.db import transaction
from django.db.models import F
from photo_web.models import Photo, Vote


class VoteService:
    @classmethod
    @transaction.atomic
    def switch_vote(cls, user, photo_id: int) -> dict:

        # Переключает голос пользователя
        # Возвращает: {'action': 'added' | 'removed', 'votes_count': int}

        # Проверяем существование фото и его статус.
        try:
            photo = Photo.objects.get(id=photo_id, status=Photo.Status.approved)
        except Photo.DoesNotExist:
            raise ValueError('Фотография не найдена или не одобрена')

        # проверяем/создаём запись голоса
        # created=True - голоса ещё не было, False - уже есть
        vote, created = Vote.objects.get_or_create(user=user, photo=photo)

        # Обновляем счётчик через F()-выражение.
        # F() вычисляет в PostgreSQL, исключая race condition.
        if created:
            action = 'added'
            Photo.objects.filter(id=photo.id).update(votes_count=F('votes_count') + 1)
            new_count = photo.votes_count + 1
        else:
            action = 'removed'
            vote.delete()
            Photo.objects.filter(id=photo.id).update(votes_count=F('votes_count') - 1)
            new_count = photo.votes_count - 1

        return {'action': action, 'votes_count': new_count}