import jwt
from django.conf import settings
from rest_framework import authentication
from rest_framework import exceptions
from .models import User

class SimpleJWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = authentication.get_authorization_header(request).split()
        if not auth_header:
            return None

        # Expect: Authorization: Bearer <token>
        if len(auth_header) != 2:
            return None

        prefix = auth_header[0].decode()
        token = auth_header[1].decode()

        if prefix.lower() != 'bearer':
            return None

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except Exception:
            raise exceptions.AuthenticationFailed('Invalid token')

        try:
            user = User.objects.get(id=payload.get("user_id"))
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed('No such user')

        return (user, None)
