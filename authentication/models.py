from django.db import models

# Create your models here.

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from rest_framework_simplejwt.tokens import RefreshToken


class UserManager(BaseUserManager):

    def create_user(self, username, email, password=None):
        if username is None:
            raise TypeError("Username is Required")
        if email is None:
            raise TypeError("Username is Required")

        user = self.model(username=username, email=self.normalize_email(email))

        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, password=None):

        if password is None:
            raise TypeError("Password cannot be empty")

        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.is_verified = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(max_length=255, unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # defining the fields that django will use by default to login (by default it takes username)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        return f'User : {self.email}'

    def tokens(self):
        refresh_token = RefreshToken.for_user(self)
        token = dict()
        token['refresh'] = str(refresh_token)
        token['access'] = str(refresh_token.access_token)
        return token








