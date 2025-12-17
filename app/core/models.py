from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models  # noqa
from typing import Any
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils.translation import gettext_lazy as _


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


class Recipe(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("user"),
    )
    title = models.CharField(max_length=255, verbose_name=_("title"))
    description = models.TextField(verbose_name=_("description"))
    duration_minute = models.PositiveSmallIntegerField(
        verbose_name=_("duration minute"), validators=[MinValueValidator(0.01)]
    )
    price = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=("price"),
        validators=[MinValueValidator(0)],
    )
    link = models.URLField(null=True, blank=True, verbose_name=_("link"))

    def __str__(self) -> str:
        return self.title

    class Meta:
        ordering = ["-pk"]


class Tag(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_("user"),
    )
    name = models.CharField(max_length=128, verbose_name=_("name"))

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["-name"]
