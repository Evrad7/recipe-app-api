from django.test import TestCase
from django.contrib.auth import get_user_model


class TestUser(TestCase):

    def test_create_user_with_email(self):
        email = "test@examble.com"
        password = "123xyzSecure"

        user = get_user_model().objects.create_user(email, password)

        user.refresh_from_db()
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)

    def test_create_user_with_normalized_email(self):

        samples = [
            ("test1@Example.com", "test1@example.com"),
            ("Test2@EXAMPLE.com", "Test2@example.com"),
            ("test3@Example.COM", "test3@example.com"),
            ("TEST4@EXAMPLE.COM", "TEST4@example.com"),
        ]

        for email, formatted_email in samples:
            user = get_user_model().objects.create_user(
                email, "123xyzPassword"
            )
            self.assertEqual(user.email, formatted_email)

    def test_not_create_user_with_invalid_email(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "123xyzPassword")

    def test_create_superuser_with_email(self):
        email = "test@example.com"
        password = "123xyzPassword"

        user = get_user_model().objects.create_superuser(
            email, password
        )  # type: ignore
        user.refresh_from_db()
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
