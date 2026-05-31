from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from photo_web.models import Photo, Vote

class VoteService:
    @classmethod
    @transaction.atomic
    def switch_vote(cls, user, photo_id: int) -> dict:
        # Получаем фото, если оно одобрено
        # select_for_update - блокирует строку на время транзакции
        try:
            photo = Photo.objects.select_for_update().get(
                id = photo_id,
                status = Photo.Status.approved)
        except ObjectDoesNotExist:
            raise ValueError('Фотография не найдена')
        
        # Проверяем голосовал ли пользователь
        vote_exist = Vote.objects.filter(user=user, photo=photo).exists()

        # Если голосовал - голос снимается
        if vote_exist:
            Vote.objects.filter(user=user, photo=photo).delete()
            photo.votes_count -= 1
            result_action = 'removed'
        
        # Если не голосовал - голос добавляется
        else:
            Vote.objects.filter(user=user, photo=photo).create()
            photo.votes_count += 1
            result_action = 'added'

        # Сохранение изменений
        # update_field - обновит конкретное поле
        photo.save(update_fields=['votes_count'])

        return {
            'action':result_action,
            'votes_count':photo.votes_count
        }


