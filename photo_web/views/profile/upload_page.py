from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render


class PhotoUploadPageView(LoginRequiredMixin, View):
    """
    Вьюха для отображения страницы загрузки фотографии.
    """
    
    def get(self, request):
        return render(request, 'photo_web/upload.html')