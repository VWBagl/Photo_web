import json
from photo_web.models import Comment
from photo_web.tests.comment.base import CommentViewsBaseTest

class CreateCommentViewTest(CommentViewsBaseTest):

    # Неавторизованный пользователь не может писать комментарий.
    def test_unauthenticated_user_rejected(self):
        response = self.client.post(
            self.create_url,
            data=json.dumps({
                'photo_id': self.photo.id,
                'text': 'Привет'
            }),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [302, 403])

    # Авторизованный пользователь может писать комментарии
    def test_create_success(self):

        # Проверка: создание нового комментария от авторизованного пользователя.
        # Вход:
        # - Авторизованный пользователь (не автор фото)
        # - photo_id одобренной фотографии
        # - Непустой текст комментария

        self.client.login(username='other', password='password123')

        response = self.client.post(
            self.create_url,
            data=json.dumps({
                'photo_id': self.photo.id,
                'text': 'Отличная фотография!'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['text'], 'Отличная фотография!')
        self.assertEqual(data['author'], 'other')
        self.assertEqual(data['photo_comments_count'], 2)

        self.assertTrue(Comment.objects.filter(id=data['id']).exists())
        self.photo.refresh_from_db()
        self.assertEqual(self.photo.comments_count, 2)

    def test_create_reply(self):

        # Проверка: создание ответа на комментарий первого уровня.
        # Вход:
        # - parent_id существующего комментария первого уровня

        self.client.login(username='other', password='password123')

        response = self.client.post(
            self.create_url,
            data=json.dumps({
                'photo_id': self.photo.id,
                'text': 'Ответ на комментарий',
                'parent_id': self.comment.id
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data['parent_id'], self.comment.id)

        reply = Comment.objects.get(id=data['id'])
        self.assertEqual(reply.parent_comment, self.comment)


    # Нельзя ответить на ответ (ограничение вложенности)
    def test_reply_to_reply_forbidden(self):
        # Вход:
        # - parent_id комментария, который сам является ответом

        self.client.login(username='other', password='password123')

        reply = Comment.objects.create(
            author=self.author,
            photo=self.photo,
            text='Ответ',
            parent_comment=self.comment
        )

        response = self.client.post(
            self.create_url,
            data=json.dumps({
                'photo_id': self.photo.id,
                'text': 'Попытка вложенного ответа',
                'parent_id': reply.id
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('первого уровня', response.json()['error'].lower())

    # Попытка отправления пустого комментария
    def test_create_empty_text(self):
        self.client.login(username='other', password='password123')

        response = self.client.post(
            self.create_url,
            data=json.dumps({
                'photo_id': self.photo.id,
                'text': '   '
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('пустым', response.json()['error'].lower())

    def test_create_text_too_long(self):
        self.client.login(username='other', password='password123')

        response = self.client.post(
            self.create_url,
            data=json.dumps({
                'photo_id': self.photo.id,
                'text': 'a' * 2001
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('слишком длинный', response.json()['error'].lower())

    # Невалидный JSON в теле запроса
    def test_create_invalid_json(self):
        # Вход:
        # - Строка "broken json" вместо валидного JSON

        self.client.login(username='other', password='password123')

        response = self.client.post(
            self.create_url,
            data='broken json',
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('json', response.json()['error'].lower())

    # Отсутствие обязательных полей photo_id или text.
    def test_create_missing_fields(self):

        # Вход:
        # - Два запроса: без photo_id и без text

        self.client.login(username='other', password='password123')

        response_no_photo = self.client.post(
            self.create_url,
            data=json.dumps({'text': 'Текст без фото'}),
            content_type='application/json'
        )
        self.assertEqual(response_no_photo.status_code, 400)

        response_no_text = self.client.post(
            self.create_url,
            data=json.dumps({'photo_id': self.photo.id}),
            content_type='application/json'
        )
        self.assertEqual(response_no_text.status_code, 400)

    # Попытка оставить комментарий к несуществующей фотографии
    def test_create_nonexistent_photo(self):
        # Вход:
        # - photo_id=99999 (не существует в БД)

        self.client.login(username='other', password='password123')

        response = self.client.post(
            self.create_url,
            data=json.dumps({
                'photo_id': 99999,
                'text': 'Комментарий'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('не найдена', response.json()['error'].lower())