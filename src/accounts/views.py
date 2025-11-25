from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import UserCreateSerializer
from .models import Role
from notifications.utils import send_email_with_record
import jwt
from django.conf import settings
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from accounts.models import User

class CreateUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        creator = request.user

        serializer = UserCreateSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        role_id = request.data.get('role_id')
        new_role = Role.objects.get(id=role_id)

        # Permission Check
        if creator.role.level <= new_role.level:
            return Response({"error": "You cannot create a user of this role"}, status=403)

        created_user_data = serializer.save()

        message = (
            f"Hello {request.data.get('first_name', '')} {request.data.get('last_name', '')},\n\n"
            f"Your account has been created.\n\n"
            f"Username: {created_user_data['username']}\n"
            f"Password: {created_user_data['generated_password']}\n\n"
            "Please change your password after first login."
        )
        
        send_email_with_record(
            email=created_user_data['email'],
            subject="Your Account Credentials",
            # message="Username: " + created_user_data['username'] +
            #         " Password: " + created_user_data['generated_password'],
            message=message,
            email_type="USER_CREDENTIALS"
        )

        return Response({"message": "User created and email sent"})
    
class LoginView(APIView):
    def post(self, request):
        identifier = request.data.get('identifier')
        password = request.data.get('password')

        # Try username
        user = authenticate(username=identifier, password=password)

        if not user:
            # Try email
            try:
                print(identifier)
                user_obj = User.objects.get(email=identifier)
                print(user_obj)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                return Response({"error": "User Doesnot exist"}, status=500)
            
            # If we found a user by email, check the password directly
            # if user_obj and user_obj.check_password(password):
                # user = user_obj

        if not user:
            return Response({"error": "Invalid credentials"}, status=401)

        payload = {"user_id": user.id}

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        return Response({"token": token})