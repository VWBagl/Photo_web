from django.db import transaction
from django.db.models import F
from photo_web.models import Comment, Photo

class CommentManageService:
    @classmethod
    @transaction.atomic
    def update(cls, user, comment_id: int, text: str) -> dict:
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            raise ValueError("Комментарий не найден")

        if comment.author != user and not user.is_moderator:
            raise ValueError("Редактировать комментарий может только автор или модератор")

        # Если text=None, (text or "") вернет "", и .strip() не вызовет ошибку
        text = (text or "").strip()
        
        if not text:
            raise ValueError("Текст комментария не может быть пустым")
        if len(text) > 2000:
            raise ValueError("Комментарий слишком длинный (макс. 2000 символов)")

        comment.text = text
        comment.save(update_fields=['text', 'updated_at'])

        return {
            'id': comment.id,
            'text': comment.text,
            'is_author': True,
            'updated_at': comment.updated_at.strftime('%d.%m.%Y %H:%M')
        }

    @classmethod
    @transaction.atomic
    def delete(cls, user, comment_id: int) -> dict:
        try:
            comment = Comment.objects.select_related('photo').get(id=comment_id)
        except Comment.DoesNotExist:
            raise ValueError("Комментарий не найден")

        if comment.author != user and not user.is_moderator:
            raise ValueError("У вас нет прав на удаление этого комментария")

        if comment.replies.exists():
            raise ValueError("Нельзя удалить комментарий, на который уже есть ответы")

        photo_id = comment.photo_id
        comment.delete()
        
        Photo.objects.filter(id=photo_id).update(comments_count=F('comments_count') - 1)
        comment.photo.refresh_from_db()

        return {
            'status': 'deleted',
            'comment_id': comment_id,
            'photo_id': photo_id,
            'photo_comments_count': comment.photo.comments_count
        }