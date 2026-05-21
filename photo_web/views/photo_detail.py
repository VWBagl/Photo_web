from django.shortcuts import render, get_object_or_404
from ..models import Photo

def photo_detail_view(request, photo_id):
    # Только одобренные фото + автор и комментарии 
    photo = get_object_or_404(
        Photo.objects.select_related('author'),
        id=photo_id,
        status=Photo.Status.approved
    )
    
    # Комментарии
    comments = (
    photo.comments.filter(parent_comment=None).select_related('author').order_by('-created_at'))

    return render(request, 'photo_web/photo_detail.html', {
        'photo': photo,
        'comments': comments,
    })