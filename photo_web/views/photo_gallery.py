from django.shortcuts import render
# заглушка редиректа, чтобы не сеить их по проекту
def gallery_view(request):
    return render(request, 'photo_web/photo_gallery.html')