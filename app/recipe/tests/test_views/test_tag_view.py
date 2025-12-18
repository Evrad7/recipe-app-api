from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Tag


def list_tag_url():
    return reverse("recipe:tag-list")


def detail_tag_url(tag_id):
    return reverse("recipe:tag-detail", args=[tag_id])


class PublicTagViewSetTestCase(APITestCase):

    def setUp(self) -> None:
        pass

    def test_list_tags_with_unauthenticated_user_should_fail(self):
        """Test unauthenticated user cannot get tags"""
        response = self.client.get(list_tag_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_tag_with_unauthenticated_should_fail(self):
        """Test unauthenticated user cannot update tags"""
        response = self.client.put(detail_tag_url(1), {"name": "X"})

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_tag_with_unauthenticated_should_fail(self):
        """Test unauthenticated user cannot delete tags"""
        response = self.client.delete(detail_tag_url(1))

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagViewSetTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            **{"email": "test@example.com", "password": "123xZPassword"}
        )

        self.client.force_authenticate(user=self.user)  # type: ignore

    def test_list_tags_with_success(self):
        """Test lisg tag successfully"""
        Tag.objects.create(user=self.user, name="Meet")
        Tag.objects.create(user=self.user, name="Fruit")

        response = self.client.get(list_tag_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tags = Tag.objects.order_by("name")
        data = response.data  # type: ignore
        self.assertEqual(len(data), 2)
        for i in range(tags.count()):
            self.assertEqual(tags[i].pk, data[i]["id"])
            self.assertEqual(tags[i].name, data[i]["name"])

    def test_list_tags_only_for_current_user(self):
        """Test should only list tag for current user"""
        another_user = get_user_model().objects.create_user(
            **{"email": "anotheruser@example.com", "password": "xyz1Password"}
        )
        Tag.objects.create(user=self.user, name="Meet")
        Tag.objects.create(user=another_user, name="Fruit")

        response = self.client.get(list_tag_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        tags = Tag.objects.filter(user=self.user).order_by("-name")
        data = response.data  # type: ignore
        self.assertEqual(len(data), 1)
        for i in range(tags.count()):
            self.assertEqual(tags[i].pk, data[i]["id"])
            self.assertEqual(tags[i].name, data[i]["name"])

    def test_update_tag_with_success(self):
        """Test should update tag with success"""
        tag = Tag.objects.create(user=self.user, name="Meet")
        payload = {"name": "Fruity"}

        response = self.client.put(detail_tag_url(tag.pk), payload)

        data = response.data  # type: ignore
        tag.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(tag.user, self.user)
        self.assertEqual(tag.pk, data["id"])
        self.assertEqual(payload["name"], data["name"])

    def test_update_tag_with_invalid_data(self):
        """Test should fail when input data are invalid"""
        tag = Tag.objects.create(user=self.user, name="Meet")
        payload = {"name": ""}

        response = self.client.put(detail_tag_url(tag.pk), payload)

        data = response.data  # type: ignore
        tag.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", data)
        self.assertNotEqual(tag.name, payload["name"])

    def test_non_owner_cannot_update_tag(self):
        """Test that one user cannot update tag for another user"""
        another_user = get_user_model().objects.create_user(
            **{"email": "anotheruser@example.com", "password": "123xZPassword"}
        )
        tag = Tag.objects.create(user=another_user, name="Dessert")

        response = self.client.put(detail_tag_url(tag.pk), {"name": "x"})

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_destroy_tag_with_success(self):
        """Test tha tag is can be deleted with success"""
        tag = Tag.objects.create(user=self.user, name="Before meal")

        response = self.client.delete(detail_tag_url(tag.pk))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_non_owner_cannot_delete_tag(self):
        """Test that one user cannot delete tag for another user"""
        another_user = get_user_model().objects.create_user(
            **{"email": "anotheruser@example.com", "password": "123xZPassword"}
        )
        tag = Tag.objects.create(user=another_user, name="Dessert")

        response = self.client.delete(detail_tag_url(tag.pk))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
