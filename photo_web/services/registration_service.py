from django.db import IntegrityError
from django.core.exceptions import ValidationError
from ..models import User

class RegistrationService:
    @staticmethod
    def create_user(username: str, password: str) -> User:

        try:
            # create_user() внутри вызывает set_password()
            return User.objects.create_user(username=username, password=password)
        except IntegrityError:
            raise ValidationError("Пользователь с таким логином уже существует.")