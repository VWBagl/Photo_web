from photo_web.models import Comment

class CommentReadService:
    @staticmethod
    def get_comments_for_photo(photo_id: int):
        return Comment.objects.filter(
            photo_id=photo_id,
            parent_comment=None
        ).select_related('author').order_by('-created_at')