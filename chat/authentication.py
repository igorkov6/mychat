from django.contrib.auth.models import User
from loguru import logger


class EmailAuthBackend(object):
    """Выполняет аутентификацию пользователя по e-mail."""

    def authenticate(self, request, username=None, password=None):
        try:
            # найти всех пользователей с этим адресом
            users = User.objects.filter(email=username)
            # найти пользователя с совпадающим паролем
            for user in users:
                if user.check_password(password):
                    return user
            return None
        except Exception:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except Exception:
            return None
