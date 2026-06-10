import json
from django.urls import reverse
from photo_web.models import Comment
from photo_web.tests.comment.base import CommentViewsBaseTest

class DeleteCommentViewTest(CommentViewsBaseTest):
    def get_manage_url(self):
        return reverse('manage_comment', kwargs={'comment_id': self.comment.id})

    def test_unauthenticated_user_rejected(self):
        response = self.client.delete(self.get_manage_url(), content_type='application/json')
        self.assertIn(response.status_code, [302, 403])

    def test_delete_by_author_success(self):
        self.client.login(username='author', password='password123')
        response = self.client.delete(self.get_manage_url(), content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'deleted')
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())
        self.photo.refresh_from_db()
        self.assertEqual(self.photo.comments_count, 0)

    def test_delete_by_moderator_success(self):
        self.client.login(username='moderator', password='password123')
        response = self.client.delete(self.get_manage_url(), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_by_other_user_forbidden(self):
        self.client.login(username='other', password='password123')
        response = self.client.delete(self.get_manage_url(), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_with_replies_forbidden(self):
        self.client.login(username='author', password='password123')
        Comment.objects.create(author=self.other, photo=self.photo, text='Ответ', parent_comment=self.comment)
        
        response = self.client.delete(self.get_manage_url(), content_type='application/json')
        self.assertEqual(response.status_code, 403)
        self.assertTrue(Comment.objects.filter(id=self.comment.id).exists())

    def test_delete_nonexistent_comment(self):
        self.client.login(username='author', password='password123')
        url = reverse('manage_comment', kwargs={'comment_id': 99999})
        response = self.client.delete(url, content_type='application/json')
        self.assertIn(response.status_code, [400, 403, 404])