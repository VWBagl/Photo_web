from django.urls import path
from .views.registration.registration import registration_view
from .views.authorization.auth import auth_view, logout_view

from .views.gallery.gallery import gallery_view, gallery_fragment_view
from .views.gallery.detail import photo_detail_view

from .views.vote.vote import SwitchVoteView

from .views.comment.create import CreateCommentView
from .views.comment.update_delete import CommentManageView

from .views.profile.photo_upload import PhotoUploadView
from .views.profile.photo_edit import PhotoEditView
from .views.profile.photo_delete import PhotoDeleteView
from .views.profile.photo_restore import PhotoRestoreView
from .views.profile.my_photos import MyPhotosView 

from .views.profile.upload_page import PhotoUploadPageView
from .views.profile.edit_page import PhotoEditPageView 

urlpatterns = [
    path('', gallery_view, name='photo_gallery'),
    path('registration/', registration_view, name='registration'),
    path('auth/', auth_view, name='auth'),
    path('logout/', logout_view, name='logout'),
    path('photo_gallery/', gallery_view, name='photo_gallery'),
    path('gallery/fragment/', gallery_fragment_view, name='gallery_fragment'),
    path('photo/<int:photo_id>/', photo_detail_view, name='photo_detail'),
    
    # Голосование - Vote
    path('api/vote/', SwitchVoteView.as_view(), name='switch_vote'),
    
    # Комментарии - Comment
    path('api/comments/create/', CreateCommentView.as_view(), name='create_comment'),
    path('api/comments/', CreateCommentView.as_view(), name='create_comment'),
    path('api/comments/<int:comment_id>/', CommentManageView.as_view(), name='manage_comment'),

    # Личный кабинет - Profile
        # API
    path('api/profile/photos/upload/', PhotoUploadView.as_view(), name='upload_photo'),
    path('api/profile/photos/<int:photo_id>/edit/', PhotoEditView.as_view(), name='edit_photo'),
    path('api/profile/photos/<int:photo_id>/delete/', PhotoDeleteView.as_view(), name='delete_photo'),
    path('api/profile/photos/<int:photo_id>/restore/', PhotoRestoreView.as_view(), name='restore_photo'),
        # Страницы
    path('profile/photos/', MyPhotosView.as_view(), name='my_photos'),
    path('profile/photos/upload/', PhotoUploadPageView.as_view(), name='upload_photo_page'), 
    path('profile/photos/<int:photo_id>/edit/', PhotoEditPageView.as_view(), name='edit_photo_page'), 

]