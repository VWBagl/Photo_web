from django.test import TestCase, Client
from django.urls import reverse
from photo_web.models import User

class AuthViewsTest(TestCase):
    
    def setUp(self):
        # Инициализация перед КАЖДЫМ тестом
        self.client = Client()
        self.url = reverse('auth')
        self.gallery_url = reverse('photo_gallery')
        
        # Создаем валидного пользователя заранее, чтобы тестировать вход
        User.objects.create_user(
            username='test_user',
            password='secure_password_123'
        )

    def test_get_auth_page(self):
        # Образение к странице
        response = self.client.get(self.url)
        
        # Статус 200 = OK
        self.assertEqual(response.status_code, 200)
        # Используется правильный шаблон
        self.assertTemplateUsed(response, 'photo_web/auth.html')

    def test_successful_login(self):
        valid_data = {
            'username': 'test_user',
            'password': 'secure_password_123'
        }
        
        # Имитируем отправку формы
        response = self.client.post(self.url, valid_data)
        
        # Проверяем редирект на галерею
        self.assertRedirects(response, self.gallery_url)
        
        # Проверяем, что сессия создана
        # Django хранит ID авторизованного юзера в сессии под ключом '_auth_user_id'
        self.assertIn('_auth_user_id', self.client.session)

    def test_login_wrong_password(self):
        wrong_data = {
            'username': 'test_user',
            'password': 'wrong_password'
        }
        
        response = self.client.post(self.url, wrong_data)
        
        # Редиректа нет, страница перезагрузилась (200)
        self.assertEqual(response.status_code, 200)
        
        # В форме есть общая ошибка (non_field_errors)
        form = response.context['form']
        self.assertTrue(len(form.non_field_errors()) > 0)
        self.assertIn("Неверный логин или пароль", str(form.errors))
        
        # Сессия НЕ создана
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_redirect_if_already_authenticated(self):
        # Сначала логинимся (вручную, чтобы создать сессию)
        self.client.login(username='test_user', password='secure_password_123')
        
        # Пытаемся зайти на страницу входа
        response = self.client.get(self.url)
        
        # Должно редиректнуть на галерею, а не показать форму снова
        self.assertRedirects(response, self.gallery_url)