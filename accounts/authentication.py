from accounts.models import User, Token


class PasswordlessAuthenticationBackend:

    @staticmethod
    def authenticate(uid):
        try:
            token = Token.objects.get(uid=uid)
        except Token.DoesNotExist:
            return None

        try:
            return User.objects.get(email=token.email)
        except User.DoesNotExist:
            return User.objects.create(email=token.email)

    # As for django 2.2.3 first argument must be pk!
    @staticmethod
    def get_user(pk=None, email=None):
        if pk is None and email is None:
            raise ValueError("You must give one argument!")
        elif email:
            try:
                return User.objects.get(email=email)
            except User.DoesNotExist:
                return None
        elif pk:
            try:
                return User.objects.get(pk=pk)
            except User.DoesNotExist:
                return None
