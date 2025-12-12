from django.test import TestCase
from django.contrib.auth import get_user_model


class TestUser(TestCase):

    def test_create_user_with_email(self):
        email = "test@examble.com"
        password = "123xyzSecure"

        user = get_user_model().objects.create_user(email, password)

        user.refresh_from_db()
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password())
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
