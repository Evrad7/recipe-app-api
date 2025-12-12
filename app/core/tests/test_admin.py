from django.http import HttpResponse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from core.models import User


class TestAdmin(TestCase):

    def setUp(self) -> None:

        self.client = Client()
        self.admin_user: User = get_user_model().objects.create_superuser(
            "admin@example.com", "123xyzPassword"
        )  # type: ignore

        self.user: User = get_user_model().objects.create_user(
            "user@example.com", "123xyzPassword", name="Job"
        )  # type: ignore

        self.client.force_login(self.admin_user)

    def test_list_users(self):
        response: HttpResponse = self.client.get(
            reverse("admin:core_user_changelist")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.name)

    def test_edit_user_page(self):
        url: str = reverse("admin:core_user_change", args=[self.user.pk])

        response: HttpResponse = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.email)
        self.assertContains(response, self.user.name)

    def test_add_user_page(self):
        url: str = reverse("admin:core_user_add")

        response: HttpResponse = self.client.get(url)

        self.assertEqual(response.status_code, 200)
