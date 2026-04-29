from django.urls import path
from .views.registration import registration_view
from .views.auth import auth_view
from .views.photo_gallery import gallery_view

urlpatterns = [
    path('registration/', registration_view, name='registration'),
    path('auth/', auth_view, name='auth'),
    path('photo_gallery/', gallery_view, name='photo_gallery')
]