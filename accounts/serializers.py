from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import AuthIdentifier, IdentifierType


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'email': {'required': True},
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        # create primary email identifier
        AuthIdentifier.objects.create(
            user=user,
            identifier=user.email,
            id_type=IdentifierType.EMAIL,
            is_primary=True,
            is_verified=False,
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'is_verified', 'date_joined']


