from django.test import TestCase
from django.contrib import auth
from accounts.models import Token
from functional_tests.base import TEST_EMAIL

User = auth.get_user_model()


class UserModelTest(TestCase):

    @staticmethod
    def test_user_is_valid_with_email_only():
        user = User(email=TEST_EMAIL)
        user.full_clean()  # should not raise

    def test_no_problem_with_auth_login(self):
        user = User.objects.create(email=TEST_EMAIL)
        user.backend = ""
        request = self.client.request().wsgi_request
        auth.login(request, user)  # should not raise


class TokenModelTest(TestCase):

    def test_links_user_with_auto_generated_uid(self):
        token1 = Token.objects.create(email="a@b.com")
        token2 = Token.objects.create(email="a@b.com")
        self.assertNotEqual(token1.uid, token2.uid)
