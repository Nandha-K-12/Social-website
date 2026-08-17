from django.test import TestCase
from django.contrib.auth.models import User
from actions.models import Action
from actions.utils import create_action
from images.models import Image


class ActionTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='alice', password='password123')
        self.user2 = User.objects.create_user(username='bob', password='password123')
        self.image = Image.objects.create(
            user=self.user1,
            title='Test Image',
            url='https://example.com/test.jpg',
            image='images/test.jpg'
        )

    def test_create_action_without_target(self):
        result = create_action(self.user1, 'has created an account')
        self.assertTrue(result)
        self.assertEqual(Action.objects.count(), 1)
        action = Action.objects.first()
        self.assertEqual(action.user, self.user1)
        self.assertEqual(action.verb, 'has created an account')
        self.assertIsNone(action.target)

    def test_create_action_with_target(self):
        result = create_action(self.user2, 'bookmarked image', self.image)
        self.assertTrue(result)
        self.assertEqual(Action.objects.count(), 1)
        action = Action.objects.first()
        self.assertEqual(action.user, self.user2)
        self.assertEqual(action.verb, 'bookmarked image')
        self.assertEqual(action.target, self.image)

    def test_duplicate_action_avoidance(self):
        # First call creates action
        res1 = create_action(self.user1, 'likes', self.image)
        self.assertTrue(res1)
        self.assertEqual(Action.objects.count(), 1)

        # Duplicate call within 1 minute is ignored
        res2 = create_action(self.user1, 'likes', self.image)
        self.assertFalse(res2)
        self.assertEqual(Action.objects.count(), 1)
