from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.authentication import PasswordlessAuthenticationBackend
from accounts.models import Token
from functional_tests.base import TEST_EMAIL

User = get_user_model()


class AuthenticationTest(TestCase):

    def test_returns_None_if_no_such_token(self):
        result = PasswordlessAuthenticationBackend().authenticate(
            "no-such_token"
        )
        self.assertIsNone(result)

    def test_returns_new_user_with_correct_email_if_token_exists(self):
        token = Token.objects.create(email=TEST_EMAIL)
        user = PasswordlessAuthenticationBackend().authenticate(token.uid)
        new_user = User.objects.get(email=TEST_EMAIL)
        self.assertEqual(user, new_user)

    def test_returns_existing_user_with_correct_email_if_token_exists(self):
        existing_user = User.objects.create(email=TEST_EMAIL)
        token = Token.objects.create(email=TEST_EMAIL)
        user = PasswordlessAuthenticationBackend().authenticate(token.uid)
        self.assertEqual(user, existing_user)


class GetUserTest(TestCase):

    @staticmethod
    def create_two_users_one_from_desired_pk_or_email(pk=None, email=None):
        User.objects.create(email="another@example.com")
        if email:
            return User.objects.create(email=email)
        else:
            return User.objects.create(pk=pk)

    def test_gets_user_by_email(self):
        desired_user = self.create_two_users_one_from_desired_pk_or_email(email=TEST_EMAIL)
        found_user = PasswordlessAuthenticationBackend().get_user(
            email=TEST_EMAIL
        )
        self.assertEqual(desired_user, found_user)

    def test_get_user_by_pk(self):
        desired_user = self.create_two_users_one_from_desired_pk_or_email(pk=5)
        found_user = PasswordlessAuthenticationBackend.get_user(5)
        self.assertEqual(desired_user, found_user)

    def test_returns_None_if_no_user_with_that_email(self):
        self.assertIsNone(
            PasswordlessAuthenticationBackend().get_user(email=TEST_EMAIL)
        )

    def test_return_None_if_no_user_with_that_pk(self):
        self.assertIsNone(
            PasswordlessAuthenticationBackend.get_user(pk=5)
        )

    def test_no_arguments_raises_value_error(self):
        with self.assertRaises(ValueError):
            PasswordlessAuthenticationBackend.get_user()
