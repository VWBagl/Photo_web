from django.urls import path
from .views.registration import registration_view

urlpatterns = [
    path('registration/', registration_view, name='registration')
    #path('auth/', ...), path('gallery/', ...)
]