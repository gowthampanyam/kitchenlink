from rest_framework import serializers
from .models import User, Role
import random, string

from rest_framework import serializers
from .models import User, Role
import random
import string

class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    date_of_birth = serializers.DateField()
    role_id = serializers.IntegerField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    def generate_password(self):
        letters = string.ascii_letters + string.digits
        return ''.join(random.choice(letters) for i in range(8))

    def create(self, validated_data):
        role = Role.objects.get(id=validated_data['role_id'])
        password = self.generate_password()

        user = User(
            username=validated_data['username'],
            email=validated_data['email'],
            date_of_birth=validated_data['date_of_birth'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=role
        )

        user.set_password(password)
        user.save()

        validated_data['generated_password'] = password
        return validated_data
