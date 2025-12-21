from decimal import Decimal
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Ingredient, Recipe


def list_ingredient_url():
    return reverse("recipe:ingredient-list")


def detail_ingredient_url(ingredient_id):
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


class PublicIngredientViewSetTestCase(APITestCase):

    def setUp(self) -> None:
        return super().setUp()

    def test_unauthenticated_actions(self):
        cases = [
            # ("post", detail_ingredient_url(1), {"name":"X"}),
            # ("get", detail_ingredient_url(1), None),
            ("get", list_ingredient_url(), None),
            ("put", detail_ingredient_url(1), {"name": "X"}),
            ("patch", detail_ingredient_url(1), {"name": "X"}),
            ("delete", detail_ingredient_url(1), None),
        ]

        for method, url, payload in cases:
            with self.subTest(method=method, url=url):

                response = getattr(self.client, method)(
                    url, payload, format="json"
                )

                self.assertEqual(
                    response.status_code, status.HTTP_401_UNAUTHORIZED
                )


class PrivateIngredientViewSetTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            **{"email": "test@example.com", "password": "123xZPassword"}
        )
        self.another_user = get_user_model().objects.create_user(
            **{"email": "anotheruser@example.com", "password": "xyz1Password"}
        )
        self.client.force_authenticate(self.user)  # type: ignore

    def test_list_ingredients_with_success(self):
        Ingredient.objects.create(user=self.user, name="Vanilla")
        Ingredient.objects.create(user=self.user, name="Sugar")

        response = self.client.get(list_ingredient_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ingredients = Ingredient.objects.filter(user=self.user).order_by(
            "name"
        )
        data = response.data  # type: ignore
        self.assertEqual(len(data), 2)
        for i, ingredient in enumerate(ingredients):
            self.assertEqual(ingredient.pk, data[i]["id"])
            self.assertEqual(ingredient.name, data[i]["name"])

    def test_list_ingredients_only_for_current_user(self):
        Ingredient.objects.create(user=self.user, name="Vanilla")
        Ingredient.objects.create(user=self.another_user, name="Sugar")

        response = self.client.get(list_ingredient_url())

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ingredients = Ingredient.objects.filter(user=self.user).order_by(
            "name"
        )
        data = response.data  # type: ignore
        self.assertEqual(len(data), 1)
        for i, ingredient in enumerate(ingredients):
            self.assertEqual(ingredient.pk, data[i]["id"])
            self.assertEqual(ingredient.name, data[i]["name"])

    def test_update_ingredient_with_success(self):
        ingredient = Ingredient.objects.create(user=self.user, name="Vanilla")
        payload = {
            "name": "Sugar",
        }

        res = self.client.put(
            detail_ingredient_url(ingredient.pk), payload, format="json"
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        data = res.data
        self.assertEqual(ingredient.name, payload["name"])
        self.assertEqual(ingredient.pk, data["id"])
        self.assertEqual(ingredient.name, data["name"])

    def test_update_ingredient_with_invalid_data(self):
        ingredient = Ingredient.objects.create(user=self.user, name="Vanilla")
        payload = {
            "name": "",
        }

        res = self.client.put(
            detail_ingredient_url(ingredient.pk), payload, format="json"
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", res.data)

    def test_non_owner_cannot_update_ingredient(self):

        ingredient = Ingredient.objects.create(
            user=self.another_user, name="Salt"
        )
        payload = {"name": "Sugar"}

        res = self.client.put(
            detail_ingredient_url(ingredient.pk), payload, format="json"
        )

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    # TODO Should test patch endpoints

    def test_destroy_ingredient_with_success(self):
        ingredient = Ingredient.objects.create(user=self.user, name="Salt")

        res = self.client.delete(detail_ingredient_url(ingredient.pk))

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Ingredient.objects.filter(user=self.user).exists())

    def test_non_owner_cannot_delete_ingredient(self):
        ingredient = Ingredient.objects.create(
            user=self.another_user, name="Salt"
        )

        res = self.client.delete(detail_ingredient_url(ingredient.pk))

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_filter_ingredients_by_assigned_recipes(self):
        """Test that only ingredients assigned with at
        least 1 recipe are returned"""
        ingredient1 = Ingredient.objects.create(user=self.user, name="Vanilla")
        ingredient2 = Ingredient.objects.create(
            user=self.user, name="Chocolate"
        )
        Ingredient.objects.create(user=self.user, name="Sugar")

        recipe1 = Recipe.objects.create(
            user=self.user,
            title="Pasta gold",
            description="Awesome pasta ...",
            duration_minute=20,
            price=Decimal("8.2"),
        )
        recipe2 = Recipe.objects.create(
            user=self.user,
            title="Big mac burger",
            description="Big burger begin ....",
            duration_minute=8,
            price=Decimal("15"),
        )

        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient2)

        res = self.client.get(list_ingredient_url(), {"assigned-only": 1})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        expected_ids = {ingredient1.pk, ingredient2.pk}
        ids = {item["id"] for item in res.data}
        self.assertSetEqual(ids, expected_ids)

    def test_filtered_ingredients_with_not_duplicate(self):
        """Test that we have not duplicate_tag_with_filtering tags"""
        ingredient1 = Ingredient.objects.create(user=self.user, name="Salt")
        Ingredient.objects.create(user=self.user, name="Oil")

        recipe1 = Recipe.objects.create(
            user=self.user,
            title="Pasta gold",
            description="Awesome pasta ...",
            duration_minute=20,
            price=Decimal("8.2"),
        )
        recipe2 = Recipe.objects.create(
            user=self.user,
            title="Big mac burger",
            description="Big burger begin ....",
            duration_minute=8,
            price=Decimal("15"),
        )

        recipe1.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient1)

        res = self.client.get(list_ingredient_url(), {"assigned-only": 1})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        expected_ids = [ingredient1.pk]
        ids = [item["id"] for item in res.data]
        self.assertListEqual(ids, expected_ids)
