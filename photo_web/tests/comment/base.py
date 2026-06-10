from django.test import TestCase, Client
from django.urls import reverse
from photo_web.models import User, Photo, Comment

# Тестовые данные
class CommentViewsBaseTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.create_url = reverse('create_comment')

        self.author = User.objects.create_user(
            username='author',
            password='password123'
        )
        self.other = User.objects.create_user(
            username='other',
            password='password123'
        )
        self.moderator = User.objects.create_user(
            username='moderator',
            password='password123'
        )
        self.moderator.is_moderator = True
        self.moderator.save()

        self.photo = Photo.objects.create(
            author=self.author,
            title='Test Photo',
            description='Test description',
            status=Photo.Status.approved,
            original_image='test/photo.jpg',
            comments_count=0
        )

        self.comment = Comment.objects.create(
            author=self.author,
            photo=self.photo,
            text='Исходный текст'
        )
        self.photo.comments_count = 1
        self.photo.save()