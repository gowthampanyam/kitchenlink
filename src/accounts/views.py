from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
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
                print(User.objects.all())
                user_obj = User.objects.get(email=identifier)
                print(user_obj)
                print(user_obj.username)
                print(user_obj.check_password(password))
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

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        """
        Delete a user by ID.
        Only Manager (role.level >= 4) or Owner (role.level >= 5) can delete a user.
        A manager cannot delete an owner or another manager.
        An owner can delete anyone except themselves.
        """

        actor = request.user  # the person performing the delete action

        # Check role
        if not actor.role or actor.role.level < 4:
            return Response(
                {"error": "Only managers or owners can delete users"},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            target_user = User.objects.get(id=pk)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Prevent deleting yourself
        if actor.id == target_user.id:
            return Response({"error": "You cannot delete your own account"}, status=status.HTTP_400_BAD_REQUEST)

        # Prevent deleting same-level or higher-level users
        if target_user.role and actor.role.level <= target_user.role.level:
            return Response(
                {"error": "You cannot delete a user with equal or higher role"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Delete and confirm
        username = target_user.username
        target_user.delete()

        return Response(
            {"message": f"User '{username}' has been deleted successfully"},
            status=status.HTTP_200_OK
        )