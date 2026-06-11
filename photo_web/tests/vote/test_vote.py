import json
from django.test import TestCase, Client
from django.urls import reverse
from photo_web.models import User, Photo, Vote

class VoteViewTest(TestCase):

    def setUp(self):
        # Подготовка тестовых данных
            # Создаём:
            # - Клиент для HTTP-запросов
            # - URL эндпоинта через reverse
            # - Обычного пользователя
            # - Одобренную фотографию

        self.client = Client()
        self.url = reverse('switch_vote')

        self.user = User.objects.create_user(
            username='test_user',
            password='password123'
        )

        self.photo = Photo.objects.create(
            author=self.user,
            title='Test Photo',
            description='Test description',
            status=Photo.Status.approved,
            original_image='test/photo.jpg',
            votes_count=0
        )

    def test_unauthenticated_user_rejected(self):
        # Проверка: неавторизованный пользователь не может голосовать.
        # Вход: POST без авторизации.
        # Ожидаемый выход: редирект (302) на страницу входа или 403.

        response = self.client.post(
            self.url,
            data=json.dumps({'photo_id': self.photo.id}),
            content_type='application/json'
        )
        self.assertIn(response.status_code, [302, 403])

    def test_first_vote_returns_added(self):

        # Проверка: первый голос пользователя создаёт запись и увеличивает счётчик.
        # Вход:
        # - Авторизованный пользователь
        # - photo_id одобренной фотографии, за которую ещё не голосовали

        self.client.login(username='test_user', password='password123')

        response = self.client.post(
            self.url,
            data=json.dumps({'photo_id': self.photo.id}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['action'], 'added')
        self.assertEqual(data['votes_count'], 1)

        self.assertTrue(Vote.objects.filter(user=self.user, photo=self.photo).exists())
        self.photo.refresh_from_db()
        self.assertEqual(self.photo.votes_count, 1)

    def test_second_vote_returns_removed(self):
        # Проверка: повторный клик по тому же фото снимает голос.
        # Вход:
        # - Авторизованный пользователь
        # - photo_id фото, за которое пользователь уже голосовал

        self.client.login(username='test_user', password='password123')

        # Предварительно ставим
        Vote.objects.create(user=self.user, photo=self.photo)
        self.photo.votes_count = 1
        self.photo.save()

        response = self.client.post(
            self.url,
            data=json.dumps({'photo_id': self.photo.id}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['action'], 'removed')
        self.assertEqual(data['votes_count'], 0)

        self.assertFalse(Vote.objects.filter(user=self.user, photo=self.photo).exists())
    
    def test_multiple_users_same_photo(self):
        user2 = User.objects.create_user(username='user2', password='pass123')
    
        self.client.login(username='test_user', password='password123')
        resp1 = self.client.post(
            self.url,
            data=json.dumps({'photo_id': self.photo.id}),
            content_type='application/json'
        )
        self.assertEqual(resp1.status_code, 200, f"First vote failed: {resp1.json()}")
    
        self.client.login(username='user2', password='pass123')
        resp2 = self.client.post(
            self.url,
            data=json.dumps({'photo_id': self.photo.id}),
            content_type='application/json'
        )
        self.assertEqual(resp2.status_code, 200, f"Second vote failed: {resp2.json()}")

        self.assertEqual(Vote.objects.filter(photo=self.photo).count(), 2)
        self.photo.refresh_from_db()
        self.assertEqual(self.photo.votes_count, 2)

    def test_invalid_json_body(self):
        # Проверка: тело запроса - не валидный JSON.
        # Вход: строка "invalid json" вместо JSON.

        self.client.login(username='test_user', password='password123')

        response = self.client.post(
            self.url,
            data='invalid json',
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('json', response.json()['error'].lower())

    def test_missing_photo_id(self):
        # Проверка: в JSON отсутствует поле photo_id.
        # Вход: {"some_field": 1}
        
        self.client.login(username='test_user', password='password123')

        response = self.client.post(
            self.url,
            data=json.dumps({'some_field': 1}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('photo_id', response.json()['error'].lower())

    def test_photo_id_wrong_type(self):
        # Проверка: photo_id передан как строка вместо числа.
        # Вход: {"photo_id": "abc"}
        
        self.client.login(username='test_user', password='password123')

        response = self.client.post(
            self.url,
            data=json.dumps({'photo_id': 'not_a_number'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    def test_photo_id_negative(self):
        self.client.login(username='test_user', password='password123')

        response = self.client.post(
            self.url,
            data=json.dumps({'photo_id': -1}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('положительным', response.json()['error'].lower())

    def test_photo_id_not_exists(self):
        # Проверка: photo_id не существует в БД.

        # Вход: {"photo_id": 99999}
    
        self.client.login(username='test_user', password='password123')

        response = self.client.post(
            self.url,
            data=json.dumps({'photo_id': 99999}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('не найдена', response.json()['error'].lower())

    def test_photo_not_approved(self):
        # Проверка: фото существует, но не в статусе approved.
        # Вход: photo_id фото в статусе moderated.
    
        self.client.login(username='test_user', password='password123')

        moderated_photo = Photo.objects.create(
            author=self.user,
            title='Moderated',
            status=Photo.Status.moderated,
            original_image='test/mod.jpg'
        )

        response = self.client.post(
            self.url,
            data=json.dumps({'photo_id': moderated_photo.id}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('не одобрена', response.json()['error'].lower())