from django.db import models  # noqa
from typing import Any
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)


class UserManager(BaseUserManager):

    def create_user(
        self,
        email: str,
        password: str | None = None,
        **extra_fields: dict[str, Any]
    ):

        if not email:
            raise ValueError("user must have email address")
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, password: str | None, **extra_fields: dict[str, Any]
    ):

        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(
        max_length=244, verbose_name="email", unique=True
    )
    name = models.CharField(max_length=255, verbose_name="name")
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
