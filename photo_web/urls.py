from django.urls import path
from .views.registration import registration_view
from .views.auth import auth_view, logout_view
from .views.photo_gallery import gallery_view, gallery_fragment_view
from .views.photo_detail import photo_detail_view
from .views.vote import switch_vote_view

urlpatterns = [
    path('', gallery_view, name='photo_gallery'),
    path('registration/', registration_view, name='registration'),
    path('auth/', auth_view, name='auth'),
    path('logout/', logout_view, name='logout'),
    path('photo_gallery/', gallery_view, name='photo_gallery'),
    path('gallery/fragment/', gallery_fragment_view, name='gallery_fragment'),
    path('photo/<int:photo_id>/', photo_detail_view, name='photo_detail'),
    path('api/vote/', switch_vote_view, name='toggle_vote'),
]