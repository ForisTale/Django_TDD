from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):

    @staticmethod
    def test_user_is_valid_with_email_only():
        user = User(email="a@b.com")
        user.full_clean() # should not raise

    # NEVER DO IT FOR NORMAL WEBSITE!!!
    # I do it now only to follow book
    def test_email_is_primary_key(self):
        user = User(email="a@b.com")
        self.assertEqual(user.pk, "a@b.com")
