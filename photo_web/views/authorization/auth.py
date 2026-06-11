from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from ...forms import AuthForm
from ...services.authorization.auth import AuthService

def auth_view(request):
    if request.user.is_authenticated:
        return redirect('photo_gallery')
    
    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            try:
                # Проверка учётных данных
                user = AuthService.authenticate_user(
                    username=form.cleaned_data['username'],
                    password=form.cleaned_data['password']
                )
                # Создание сессии
                login(request, user)
                messages.success(request, "Вы успешно вошли в систему!")
                # Редирект на авторизацию
                return redirect('photo_gallery')
            except Exception as e:
                # Вывод ошибки в non_field_errors
                form.add_error(None, str(e))
    else:
        form = AuthForm()
        
    return render(request, 'photo_web/auth.html', {'form': form})

def logout_view(request):
    logout(request)  # Очищает сессию
    return redirect('auth') 