from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from users.models import Contact, Profile
from actions.models import Action
from actions.utils import create_action


class UserFollowTests(TestCase):
    def setUp(self):
        self.user_a = User.objects.create_user(username='alice', password='password123')
        self.user_b = User.objects.create_user(username='bob', password='password123')
        # Create profiles
        Profile.objects.get_or_create(user=self.user_a)
        Profile.objects.get_or_create(user=self.user_b)

    def test_contact_relationship_and_following(self):
        # Alice follows Bob
        Contact.objects.create(user_from=self.user_a, user_to=self.user_b)

        # Verify following and followers
        self.assertIn(self.user_b, self.user_a.following.all())
        self.assertIn(self.user_a, self.user_b.followers.all())

        # Verify asymmetry (Bob does not automatically follow Alice)
        self.assertNotIn(self.user_a, self.user_b.following.all())
        self.assertNotIn(self.user_b, self.user_a.followers.all())

    def test_user_follow_ajax_view(self):
        self.client.login(username='alice', password='password123')
        
        # Test follow via AJAX
        response = self.client.post(
            reverse('users:user_follow'),
            {'id': self.user_b.id, 'action': 'follow'},
            headers={'x-requested-with': 'XMLHttpRequest'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})
        self.assertTrue(Contact.objects.filter(user_from=self.user_a, user_to=self.user_b).exists())
        # Verify action was logged
        self.assertTrue(Action.objects.filter(user=self.user_a, verb='is following').exists())

        # Test unfollow via AJAX
        response = self.client.post(
            reverse('users:user_follow'),
            {'id': self.user_b.id, 'action': 'unfollow'},
            headers={'x-requested-with': 'XMLHttpRequest'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok'})
        self.assertFalse(Contact.objects.filter(user_from=self.user_a, user_to=self.user_b).exists())

    def test_dashboard_feed_with_following(self):
        self.client.login(username='alice', password='password123')
        # Alice follows Bob
        Contact.objects.create(user_from=self.user_a, user_to=self.user_b)
        
        # Bob creates an action
        create_action(self.user_b, 'has created an account')
        
        # Alice views dashboard
        response = self.client.get(reverse('users:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'has created an account')
        self.assertContains(response, 'bob')
