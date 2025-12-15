from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from core.models import User
from user.serializers import (
    BaseUserSerializer,
    TokenSerializer,
    CreateUserSerializer,
    UpdateUserSerializer,
)


class BaseUserSerializerTestCase(APITestCase):

    def setUp(self) -> None:
        self.data = {"email": "test@example.com", "name": "Test"}

    def test_validate_short_password(self):
        data = {**self.data, "password": "123Pa"}
        user = get_user_model()(**data)
        serializer = BaseUserSerializer(data=data, context={"user": user})

        self.assertFalse(serializer.is_valid())

        self.assertEqual(
            serializer.errors["password"][0].code, "password_too_short"
        )

    def test_validate_only_digit_password(self):
        data = {**self.data, "password": "8545269"}
        user = get_user_model()(**data)

        serializer = CreateUserSerializer(data=data, context={"user": user})

        self.assertFalse(serializer.is_valid())

        self.assertEqual(
            serializer.errors["password"][0].code, "password_entirely_numeric"
        )

    def test_validate_similarity_email_password(self):
        data = {**self.data, "password": "test@example.com"}
        user = get_user_model()(**data)
        serializer = CreateUserSerializer(data=data, context={"user": user})

        self.assertFalse(serializer.is_valid())

        self.assertEqual(
            serializer.errors["password"][0].code, "password_too_similar"
        )


class CreateUserSerializerTestCase(APITestCase):

    def setUp(self) -> None:
        self.data = {
            "email": "test@exemple.com",
            "password": "123xZStrongPassword",
            "name": "Test",
        }

    def test_context_user_created_for_validation(self):

        serializer = CreateUserSerializer(data=self.data)

        self.assertTrue(serializer.is_valid())
        user = serializer.context["user"]
        self.assertEqual(user.name, self.data["name"])
        self.assertEqual(user.email, self.data["email"])

    def test_create_user_with_success(self):
        serializer = CreateUserSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()

        self.assertEqual(user.email, self.data["email"])
        self.assertEqual(user.name, self.data["name"])
        self.assertTrue(user.check_password(self.data["password"]))
        self.assertNotEqual(user.password, self.data["password"])


class UpdateUserSerializerTestCase(APITestCase):

    def setUp(self) -> None:
        self.data = {
            "email": "test@exemple.com",
            "password": "123xZStrongPassword",
            "name": "Test",
        }

        self.user = get_user_model().objects.create_user(**self.data)

    def test_partial_update_user_with_success(self):
        data = {"name": "Updated name", "password": "UpdatedXZtrongPassword"}
        serializer = UpdateUserSerializer(
            instance=self.user, data=data, partial=True
        )
        serializer.is_valid()

        user: User = serializer.save()  # type: ignore

        self.assertEqual(user.name, data["name"])
        self.assertTrue(user.check_password(data["password"]))

    def test_partial_update_user_with_no_allowed_field(self):
        data = {"email": "updated@example.com"}

        serializer = UpdateUserSerializer(
            instance=self.user, data=data, partial=True
        )

        self.user.refresh_from_db()
        self.assertTrue(serializer.is_valid())
        self.assertNotIn("email", serializer.validated_data)  # type: ignore
        self.assertEqual(self.user.email, self.data["email"])


class TokenSerializerTestCase(APITestCase):

    def test_validate_valid_credentials(self):
        payload = {
            "email": "test@example.com",
            "password": "123SecurePassword",
        }
        user = get_user_model().objects.create_user(**payload)

        serializer = TokenSerializer(data=payload)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["user"], user)

    def test_validate_invalid_credentials(self):
        get_user_model().objects.create_user(
            **{
                "email": "test@example.com",
                "password": "123SecurePassword",
            }
        )
        payloads = [
            {"email": "test@example.com", "password": "InvalidePassword"},
            {"email": "invalid@example.com", "password": "123SecurePassword"},
            {"email": "invalid@example.com", "password": "InvalidePassword"},
        ]

        for payload in payloads:
            serializer = TokenSerializer(data=payload)

            self.assertFalse(serializer.is_valid())
            self.assertEqual(
                serializer.errors["non_field_errors"][0].code, "authorization"
            )
