from rest_framework import serializers
from .models import User

from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed


class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(max_length=68, min_length=6, write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def validate(self, attrs):
        username = attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError("Username must be alphanumeric")

        return attrs

    def create(self, data):
        return User.objects.create_user(**data)


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(min_length=5)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    username = serializers.CharField(max_length=255, read_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'access_token', 'refresh_token']

    def validate(self, attrs):
        email = attrs.get('email', '')
        password = attrs.get('password', '')

        user = authenticate(email=email, password=password)

        if not user:
            raise AuthenticationFailed("Invalid credentials , please retry!")

        token = user.tokens()

        return {
            'email': email,
            'username': user.username,
            'access_token': token['access'],
            'refresh_token': token['refresh'],
        }