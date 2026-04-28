from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from ..forms import RegistrationForm
from ..services.registration_service import RegistrationService

def registration_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = RegistrationService.create_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password1'],
                )
                login(request, user)
                messages.success(request, "Регистрация прошла успешно!")
                # Временно: потом 'photo_gallery'
                return redirect('registration') 
            except Exception:
                messages.error(request, "Ошибка при создании аккаунта. Попробуйте позже.")
    else:
        form = RegistrationForm()
        
    return render(request, 'photo_web/registration.html', {'form': form})