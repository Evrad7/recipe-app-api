from typing import Any
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import User


class PublicUserTestCase(APITestCase):

    CREATE_USER_URL = reverse("user:create")
    TOKEN_USER_URL = reverse("user:token")
    PROFILE_USER_URL = reverse("user:me")

    def setUp(self) -> None:
        self.payload = {
            "email": "test@example.com",
            "password": "x12jklPassword785",
            "name": "Test",
        }

    def test_create_user(self):
        response = self.client.post(self.CREATE_USER_URL, self.payload)

        data: dict[str, Any] = response.data  # type: ignore

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user: User = get_user_model().objects.get(
            email=self.payload["email"])  # type: ignore
        self.assertTrue(user.check_password(self.payload["password"]))
        self.assertEqual(user.name, data["name"])
        self.assertEqual(user.email, data["email"])
        self.assertNotIn("password", data)

    def test_create_user_with_existing_mail(self):
        get_user_model().objects.create_user(**self.payload)

        response = self.client.post(self.CREATE_USER_URL, self.payload)

        data: dict[str, Any] = response.data  # type: ignore
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        users_count = (
            get_user_model()
            .objects.filter(email=self.payload["email"])
            .count()
        )
        self.assertEqual(users_count, 1)
        self.assertIn("email", data)

    def test_create_token_with_success(self):
        get_user_model().objects.create_user(**self.payload)
        payload = {
            "email": self.payload["email"],
            "password": self.payload["password"],
        }

        response = self.client.post(self.TOKEN_USER_URL, payload)

        data: dict[str, Any] = response.data  # type: ignore
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(data["token"])

    def test_create_token_with_invalid_credentials(self):
        payload = {"email": self.payload["email"], "password": "wrongpassword"}

        response = self.client.post(self.TOKEN_USER_URL, payload)

        data: dict[str, Any] = response.data  # type: ignore
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertTrue(data["non_field_errors"])

    def test_create_token_with_missing_email(self):
        payload = {"password": "wrongpassword"}

        response = self.client.post(self.TOKEN_USER_URL, payload)
        data: dict[str, Any] = response.data  # type: ignore
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", data)
        self.assertTrue(data["email"])

    def test_create_token_with_missing_password(self):
        payload = {"email": "test@example.com"}

        response = self.client.post(self.TOKEN_USER_URL, payload)
        data: dict[str, Any] = response.data  # type: ignore
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", data)
        self.assertTrue(data["password"])

    def test_retrieve_profile_unauthenticated(self):
        response = self.client.get(self.PROFILE_USER_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.headers["WWW-Authenticate"], "Token")


class PrivateUserTestCase(APITestCase):

    PROFILE_USER_URL = reverse("user:me")

    def setUp(self) -> None:
        self.payload = {
            "email": "test@example.com",
            "password": "123XZStrongPassword",
            "name": "Test",
        }
        self.user = get_user_model().objects.create_user(**self.payload)

        self.client.force_authenticate(user=self.user)  # type: ignore

    def test_retrieve_profile_with_success(self):
        response = self.client.get(self.PROFILE_USER_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.check_password(self.payload["password"]))
        self.assertEqual(
            response.data,
            {  # type: ignore
                "email": self.user.email,
                "name": self.user.name,  # type: ignore
            },
        )

    def test_partial_update_profile_with_success(self):
        data = {
            "name": "Updated Name",
            "password": "Updated123XZStrongPassword",
        }

        response = self.client.patch(self.PROFILE_USER_URL, data)

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user.name, data["name"])  # type: ignore
        self.assertTrue(self.user.check_password(data["password"]))

    def test_not_authorized_put_method_endpoint(self):
        response = self.client.put(self.PROFILE_USER_URL, {})

        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_not_authorized_post_method_endpoint(self):
        response = self.client.post(self.PROFILE_USER_URL, {})

        self.assertEqual(
            response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )
