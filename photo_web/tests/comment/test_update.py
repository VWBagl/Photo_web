import json
from django.urls import reverse
from photo_web.tests.comment.base import CommentViewsBaseTest

class UpdateCommentViewTest(CommentViewsBaseTest):
    def get_manage_url(self):
        return reverse('manage_comment', kwargs={'comment_id': self.comment.id})

    def test_update_by_author_success(self):
        self.client.login(username='author', password='password123')
        response = self.client.patch(
            self.get_manage_url(),
            data=json.dumps({'text': 'Обновлённый текст'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, 'Обновлённый текст')

    def test_update_by_moderator_success(self):
        self.client.login(username='moderator', password='password123')
        response = self.client.patch(
            self.get_manage_url(),
            data=json.dumps({'text': 'Отредактировано модератором'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, 'Отредактировано модератором')

    def test_update_by_other_user_forbidden(self):
        self.client.login(username='other', password='password123')
        response = self.client.patch(
            self.get_manage_url(),
            data=json.dumps({'text': 'Чужое редактирование'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, 'Исходный текст')

    def test_update_empty_text(self):
        self.client.login(username='author', password='password123')
        response = self.client.patch(
            self.get_manage_url(),
            data=json.dumps({'text': ''}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403) # ValueError -> 403 в текущей архитектуре
        self.assertIn('пустым', response.json()['error'].lower())

    def test_update_nonexistent_comment(self):
        self.client.login(username='author', password='password123')
        url = reverse('manage_comment', kwargs={'comment_id': 99999})
        response = self.client.patch(
            url,
            data=json.dumps({'text': 'Новый текст'}),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [400, 403, 404])