from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

class AuthService:
    @staticmethod
    def authenticate_user(username: str, password: str):
        # Проверяет логин и пароль через встроенный механизм Django.
        # Возвращает объект User или вызывает ValidationError.

        # authenticate() автоматически сравнивает хэш пароля из БД с введённым
        user = authenticate(username=username, password=password)
        if user is None:
            raise ValidationError("Неверный логин или пароль.")
        return user