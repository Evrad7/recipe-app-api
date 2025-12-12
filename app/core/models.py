from django.db import models  # noqa
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError("user must have email address")


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(max_length=244, verbose_name="email")
    name = models.CharField(max_length=255, verbose_name="name")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
