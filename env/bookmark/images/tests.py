from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from images.models import Image


class ImageModelAndViewsTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password123')
        self.user2 = User.objects.create_user(username='user2', password='password123')
        self.image = Image.objects.create(
            user=self.user1,
            title='Sunset Beach',
            url='https://example.com/sunset.jpg',
            image='images/sunset.jpg'
        )

    def test_total_likes_denormalization_signal(self):
        # Initially 0 likes
        self.assertEqual(self.image.total_likes, 0)

        # User 1 likes the image
        self.image.users_like.add(self.user1)
        self.image.refresh_from_db()
        self.assertEqual(self.image.total_likes, 1)

        # User 2 likes the image
        self.image.users_like.add(self.user2)
        self.image.refresh_from_db()
        self.assertEqual(self.image.total_likes, 2)

        # User 1 unlikes the image
        self.image.users_like.remove(self.user1)
        self.image.refresh_from_db()
        self.assertEqual(self.image.total_likes, 1)

    def test_image_detail_and_ranking_views(self):
        self.client.login(username='user1', password='password123')
        
        # Test Detail View
        detail_url = self.image.get_absolute_url()
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sunset Beach')

        # Test Ranking View
        ranking_url = reverse('images:ranking')
        response = self.client.get(ranking_url)
        self.assertEqual(response.status_code, 200)
