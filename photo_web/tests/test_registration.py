from django.test import TestCase, Client
from django.urls import reverse
from photo_web.models import User

class RegistrationViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        # обращение к маршуруту по его имени
        self.url = reverse('registration')
        self.auth_url = reverse('auth')

    def test_get_registration_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        # Проверка используемого шаблона
        self.assertTemplateUsed(response, 'photo_web/registration.html')
        self.assertIn('form', response.context)

    def test_successful_registration_post(self):
        valid_data = {
            'username': 'new_user',
            'password': 'strong_password_123',
            'password_confirm': 'strong_password_123'
        }
        # Отправка данных формы
        response = self.client.post(self.url, valid_data)
        
        # Проверка редиректа на страницу входа
        self.assertRedirects(response, self.auth_url)
        # Проверка наличия записи в БД
        self.assertTrue(User.objects.filter(username='new_user').exists())

    def test_registration_validation_error_duplicate(self):
        # Добавляем пользователя для создания конфликта
        User.objects.create_user(username='existing_user', password='pass')
        data = {
            'username': 'existing_user',
            'password': 'pass',
            'password_confirm': 'pass'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        
        # Проверяем наличие ошибки в from.errors
        self.assertIn("Пользователь с таким логином уже существует", str(form.errors))

    def test_registration_validation_error_password_mismatch(self):
        data = {
            'username': 'mismatch_user',
            'password': 'password1',
            'password_confirm': 'password2'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        
        # Ищем текст ошибки form.errors
        self.assertIn("Пароли не совпадают", str(form.errors))