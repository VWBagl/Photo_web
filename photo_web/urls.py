from django.urls import path
from .views.registration import registration_view
from .views.auth import auth_view, logout_view
from .views.photo_gallery import gallery_view, gallery_fragment_view
from .views.photo_detail import photo_detail_view
from .views.vote import SwitchVoteView
from .views.comment.create import CreateCommentView
from .views.comment.update_delete import CommentManageView

urlpatterns = [
    path('', gallery_view, name='photo_gallery'),
    path('registration/', registration_view, name='registration'),
    path('auth/', auth_view, name='auth'),
    path('logout/', logout_view, name='logout'),
    path('photo_gallery/', gallery_view, name='photo_gallery'),
    path('gallery/fragment/', gallery_fragment_view, name='gallery_fragment'),
    path('photo/<int:photo_id>/', photo_detail_view, name='photo_detail'),
    
    # Голосование
    path('api/vote/', SwitchVoteView.as_view(), name='switch_vote'),
    
    # Комментарии
    path('api/comments/create/', CreateCommentView.as_view(), name='create_comment'),
    path('api/comments/', CreateCommentView.as_view(), name='create_comment'),
    path('api/comments/<int:comment_id>/', CommentManageView.as_view(), name='manage_comment'),
]