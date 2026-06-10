from django.db import transaction
from django.db.models import F
from photo_web.models import Photo, Comment

class CommentCreateService:
    @classmethod
    @transaction.atomic
    def create(cls, user, photo_id: int, text: str, parent_id: int = None) -> dict:
        try:
            photo = Photo.objects.get(id=photo_id, status=Photo.Status.approved)
        except Photo.DoesNotExist:
            raise ValueError("Фотография не найдена или не одобрена")

        # ИСПРАВЛЕНИЕ: Безопасная обработка None. 
        # Если text=None, выражение (text or "") вернет "", и .strip() не вызовет ошибку.
        text = (text or "").strip()
        
        if not text:
            raise ValueError("Текст комментария не может быть пустым")
        if len(text) > 2000:
            raise ValueError("Комментарий слишком длинный (макс. 2000 символов)")

        parent = None
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id, photo=photo)
                if parent.parent_comment is not None:
                    raise ValueError("Ответы допускаются только на комментарии первого уровня")
            except Comment.DoesNotExist:
                raise ValueError("Родительский комментарий не найден или не относится к этой фотографии")

        comment = Comment.objects.create(
            author=user, photo=photo, text=text, parent_comment=parent
        )
        
        Photo.objects.filter(id=photo_id).update(comments_count=F('comments_count') + 1)
        photo.refresh_from_db()

        return {
            'id': comment.id, 'text': comment.text,
            'author': comment.author.username,
            'is_author': True,
            'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M'),
            'parent_id': parent.id if parent else None,
            'photo_comments_count': photo.comments_count
        }