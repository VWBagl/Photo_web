from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from ..forms import RegistrationForm
from ..services.registration_service import RegistrationService

def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = RegistrationService.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password'],
                )
                messages.success(request, "Регистрация прошла успешно!")
                return redirect('auth')
            except ValidationError as e:
                form.add_error(None, e.message)
            except Exception:
                messages.error(request, "Ошибка при создании аккаунта. Попробуйте позже.")
    else:
        form = RegistrationForm()

    return render(request, 'photo_web/registration.html', {'form': form})