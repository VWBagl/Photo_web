from django.db import transaction
from django.db.models import F
from photo_web.models import Photo, Comment


class CommentService:
    @classmethod
    @transaction.atomic
    def create_comment(cls, user, photo_id: int, text: str, parent_id: int = None) -> dict:
        try:
            photo = Photo.objects.get(id=photo_id, status=Photo.Status.approved)
        except Photo.DoesNotExist:
            raise ValueError("Фотография не найдена или не одобрена")

        text = text.strip()
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
        photo.refresh_from_db() # Получаем актуальный счётчик после F()-обновления

        return {
            'id': comment.id, 'text': comment.text,
            'author': comment.author.username,
            'is_author': True,
            'created_at': comment.created_at.strftime('%d.%m.%Y %H:%M'),
            'parent_id': parent.id if parent else None,
            'photo_comments_count': photo.comments_count
        }

    @classmethod
    @transaction.atomic
    def delete_comment(cls, user, comment_id: int) -> dict:
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

    @classmethod
    @transaction.atomic
    def update_comment(cls, user, comment_id: int, text: str) -> dict:
        try:
            comment = Comment.objects.get(id=comment_id)
        except Comment.DoesNotExist:
            raise ValueError("Комментарий не найден")

        if comment.author != user and not user.is_moderator:
            raise ValueError("Редактировать комментарий может только автор или модератор")

        text = text.strip()
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

    @staticmethod
    def get_comments_for_photo(photo_id: int):
        return Comment.objects.filter(
            photo_id=photo_id,
            parent_comment=None
        ).select_related('author').order_by('-created_at')