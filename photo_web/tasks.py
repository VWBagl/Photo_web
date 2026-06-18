# Проверка работы
import time
from celery import shared_task

@shared_task
def test_celery_task(message: str):
    print(f"\n[Celery] Начал выполнять задачу: {message}")
    time.sleep(3)  # Имитация работы
    print(f"[Celery] Задача завершена: {message.upper()}")
    return f"Done: {message}"

from django.utils import timezone
from photo_web.models import Photo
import os


@shared_task
def process_scheduled_deletions():
    """
    Периодическая задача: удаляет фотографии, у которых наступило время scheduled_deletion_at.
    Вызывается каждые N минут через Celery Beat.
    """
    now = timezone.now()
    
    # Находим все фото, которые должны быть удалены
    photos_to_delete = Photo.objects.filter(
        status=Photo.Status.scheduled_deletion,
        scheduled_deletion_at__lte=now
    )
    
    deleted_count = 0
    for photo in photos_to_delete:
        try:
            # Удаляем файлы
            if photo.original_image:
                photo.original_image.delete()
            if photo.previous_image:
                photo.previous_image.delete()
            
            # Удаляем запись из БД
            photo.delete()
            deleted_count += 1
            
        except Exception as e:
            print(f"Ошибка при удалении фото ID={photo.id}: {e}")
    
    if deleted_count > 0:
        print(f"Удалено фотографий: {deleted_count}")
    
    return deleted_count