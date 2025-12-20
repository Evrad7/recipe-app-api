from decimal import Decimal
from io import BytesIO
from typing import Any
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import QuerySet
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from PIL import Image
from core.models import Ingredient, Recipe, Tag


def list_recipe_url():
    return reverse("recipe:recipe-list")


def detail_recipe_url(recipe_id):
    return reverse("recipe:recipe-detail", args=[recipe_id])


def detail_upload_image_recipe_url(recipe_id):
    return reverse("recipe:recipe-upload_image", args=[recipe_id])


def create_recipe(user, **kwargs: dict[str, Any | None]) -> Recipe:

    data: dict[str, Any] = {
        "title": "Pizza Capotchino",
        "description": "Long description of Pizza capotchino",
        "duration_minute": 7,
        "price": Decimal("9.6"),
    } | kwargs
    recipe: Recipe = Recipe.objects.create(user=user, **data)
    return recipe


class PublicRecipeViewSetTestCase(APITestCase):

    def test_create_recipe_unauthenticated(self):
        response = self.client.post(list_recipe_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_recipes_unauthenticated(self):

        response = self.client.get(list_recipe_url())

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeViewSetTestCase(APITestCase):

    def setUp(self) -> None:

        self.user = get_user_model().objects.create_user(
            **{
                "email": "test@example.com",
                "password": "123xZStrongPassword",
                "name": "Test",
            }
        )

        self.client.force_authenticate(user=self.user)  # type: ignore

    def test_create_recipe_with_success(self):
        payload = {
            "title": "Mozarilla",
            "description": "Long description of Mozarilla",
            "duration_minute": 5,
            "price": "10.5",
        }

        response = self.client.post(list_recipe_url(), payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe: Recipe = Recipe.objects.last()  # type: ignore
        data = response.data  # type: ignore
        self.assertEqual(recipe.user, self.user)
        self.assertEqual(recipe.pk, data["id"])
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.description, payload["description"])
        self.assertEqual(recipe.price, Decimal(payload["price"]))
        self.assertNotIn("user", data)

    def test_create_recipe_with_incorrect_data(self):

        payload = {
            "title": "",
            "description": "Long descdription of Tortillas",
            "duration_minute": 7,
        }

        response = self.client.post(list_recipe_url(), payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.data  # type: ignore
        self.assertIn("title", data)
        self.assertIn("price", data)

    def test_list_recipes_with_success(self):
        create_recipe(self.user)
        create_recipe(
            self.user,
            **{
                "title": "Pasta gold",
                "description": "description for pasta gold",
                "duration_minute": 20,
                "price": Decimal(5.9),
                "link": "https://example.com",
            }
        )

        response = self.client.get(list_recipe_url())

        recipes: QuerySet[Recipe] = Recipe.objects.order_by("-pk")
        data = response.data  # type: ignore
        self.assertEqual(recipes.count(), 2)
        for i in range(recipes.count()):
            self.assertEqual(recipes[i].user, self.user)
            self.assertEqual(recipes[i].pk, data[i]["id"])
            self.assertEqual(recipes[i].title, data[i]["title"])
            self.assertEqual(
                recipes[i].duration_minute, data[i]["duration_minute"]
            )
            self.assertEqual(str(recipes[i].price), data[i]["price"])
            self.assertEqual(recipes[i].link, data[i]["link"])

    def test_list_recipes_only_for_current_user(self):
        create_recipe(self.user)
        another_user = get_user_model().objects.create(
            **{
                "email": "anotheruser@example.com",
                "password": "123xZPassword",
            }
        )
        create_recipe(
            another_user,
            **{
                "title": "Pasta gold",
                "description": "description for pasta gold",
                "duration_minute": 20,
                "price": Decimal(5.9),
            }
        )

        response = self.client.get(list_recipe_url())

        recipes: QuerySet[Recipe] = Recipe.objects.filter(
            user=self.user
        ).order_by("-pk")
        data = response.data  # type: ignore
        self.assertEqual(recipes.count(), 1)
        for i in range(recipes.count()):
            self.assertEqual(recipes[i].user, self.user)
            self.assertEqual(recipes[i].pk, data[i]["id"])
            self.assertEqual(recipes[i].title, data[i]["title"])
            self.assertEqual(
                recipes[i].duration_minute, data[i]["duration_minute"]
            )
            self.assertEqual(str(recipes[i].price), data[i]["price"])

    def test_retrieve_recipe_with_success(self):
        recipe = create_recipe(self.user)

        response = self.client.get(detail_recipe_url(recipe.pk))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data  # type: ignore
        self.assertEqual(recipe.pk, data["id"])
        self.assertEqual(recipe.title, data["title"])
        self.assertEqual(recipe.description, data["description"])
        self.assertEqual(recipe.duration_minute, data["duration_minute"])
        self.assertEqual(recipe.price, Decimal(data["price"]))

    def test_update_recipe_with_success(self):
        recipe = create_recipe(self.user)
        payload = {
            "title": "Tortizza",
            "description": "Long description of Tortilla",
            "duration_minute": 9,
            "price": "20.8",
            "link": "http://example.com",
        }

        response = self.client.put(detail_recipe_url(recipe.pk), payload)

        recipe.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data  # type: ignore
        self.assertEqual(recipe.user, self.user)
        self.assertEqual(recipe.pk, data["id"])
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.description, payload["description"])
        self.assertEqual(recipe.duration_minute, payload["duration_minute"])
        self.assertEqual(recipe.price, Decimal(payload["price"]))
        self.assertEqual(recipe.link, payload["link"])

    def test_only_owner_update_recipe(self):
        another_user = get_user_model().objects.create_user(
            **{"email": "another@example.com", "password": "123xZPassword"}
        )
        recipe = create_recipe(another_user)

        response = self.client.put(detail_recipe_url(recipe.pk), {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_patch_recipe_with_success(self):
        recipe = create_recipe(self.user)
        payload = {
            "title": "Tortilla name updated",
            "link": "https://patched.example.com",
        }

        response = self.client.patch(detail_recipe_url(recipe.pk), payload)

        recipe.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data  # type: ignore
        self.assertEqual(recipe.user, self.user)
        self.assertEqual(recipe.pk, data["id"])
        self.assertEqual(recipe.title, payload["title"])
        self.assertEqual(recipe.description, data["description"])
        self.assertEqual(recipe.duration_minute, data["duration_minute"])
        self.assertEqual(recipe.price, Decimal(data["price"]))
        self.assertEqual(recipe.link, payload["link"])

    def test_only_owner_patch_recipe(self):
        another_user = get_user_model().objects.create_user(
            **{"email": "another@example.com", "password": "123xZPassword"}
        )
        recipe = create_recipe(another_user)

        response = self.client.patch(detail_recipe_url(recipe.pk), {})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_recipe_with_sucess(self):
        recipe = create_recipe(self.user)

        response = self.client.delete(detail_recipe_url(recipe.pk))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(pk=recipe.pk).exists())

    def test_only_owner_delete_recipe(self):
        another_user = get_user_model().objects.create_user(
            **{"email": "another@example.com", "password": "123xZPassword"}
        )
        recipe = create_recipe(another_user)

        response = self.client.delete(detail_recipe_url(recipe.pk))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_recipe_with_tags(self):
        payload = {
            "title": "Mozarilla",
            "description": "Long description of Mozarilla",
            "duration_minute": 5,
            "price": "10.5",
            "tags": [{"name": "Fruit"}, {"name": "Meet"}],
        }

        response = self.client.post(list_recipe_url(), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe: Recipe = Recipe.objects.get(
            user=self.user, title=payload["title"]
        )
        data = response.data  # type: ignore
        tags = recipe.tags.order_by("name")
        self.assertEqual(recipe.pk, data["id"])
        self.assertSetEqual(
            set(tags.values_list("name", flat=True)),
            {tag["name"] for tag in payload["tags"]},
        )
        self.assertSetEqual(
            {tag["name"] for tag in data["tags"]},
            {tag["name"] for tag in payload["tags"]},
        )

    def test_update_recipe_with_tags(self):
        tag = Tag.objects.create(user=self.user, name="Fruit")
        recipe = create_recipe(self.user)
        payload = {
            "title": "Mozarilla",
            "tags": [{"name": tag.name}, {"name": "Meet"}],
        }

        response = self.client.patch(
            detail_recipe_url(recipe.pk), payload, format="json"
        )

        self.assertTrue(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        data = response.data  # type: ignore
        tags = recipe.tags.order_by("name")
        self.assertEqual(recipe.pk, data["id"])
        self.assertIn(tag, tags)
        self.assertEqual(
            set(tags.values_list("name", flat=True)),
            {tag["name"] for tag in payload["tags"]},
        )
        self.assertSetEqual(
            {tag["name"] for tag in data["tags"]},
            {tag["name"] for tag in payload["tags"]},
        )

    def test_create_recipe_with_ingredients(self):
        payload = {
            "title": "Mozarilla",
            "description": "Long description of Mozarilla",
            "duration_minute": 5,
            "price": "10.5",
            "ingredients": [{"name": "Salt"}, {"name": "Spice"}],
        }

        res = self.client.post(list_recipe_url(), payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(user=self.user, title=payload["title"])
        data = res.data  # type: ignore
        ingredients = recipe.ingredients.order_by("name")
        self.assertEqual(ingredients.count(), 2)
        self.assertEqual(recipe.pk, data["id"])
        self.assertSetEqual(
            set(ingredients.values_list("name", flat=True)),
            {ingredient["name"] for ingredient in payload["ingredients"]},
        )
        self.assertSetEqual(
            {ingredient["name"] for ingredient in data["ingredients"]},
            {ingredient["name"] for ingredient in payload["ingredients"]},
        )

    def test_update_recipe_with_ingredients(self):
        ingredient1 = Ingredient.objects.create(user=self.user, name="Milk")
        recipe = create_recipe(self.user)
        recipe.ingredients.add(ingredient1)
        payload = {
            "ingredients": [{"name": ingredient1.name}, {"name": "Flour"}]
        }

        res = self.client.patch(
            detail_recipe_url(recipe.pk), payload, format="json"
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data  # type: ignore
        ingredients = recipe.ingredients.order_by("name")
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertSetEqual(
            {ingredient["name"] for ingredient in payload["ingredients"]},
            set(ingredients.values_list("name", flat=True)),
        )
        self.assertSetEqual(
            {ingredient["name"] for ingredient in payload["ingredients"]},
            {ingredient["name"] for ingredient in data["ingredients"]},
        )


@override_settings(MEDIA_ROOT="/tmp")
class PrivateImageRecipeTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            **{"email": "test@example.com", "password": "123xZPassword"}
        )
        self.recipe = create_recipe(user=self.user)

        self.client.force_authenticate(self.user)

    def tearDown(self) -> None:
        self.recipe.image.delete(save=False)

    def test_upload_image_recipe_with_success(self):
        recipe = create_recipe(self.user, image=None)
        buffer = BytesIO()
        image = Image.new("RGB", (10, 10), color="green")
        image.save(buffer, format="PNG")
        buffer.seek(0)

        image = SimpleUploadedFile(
            "test.png", buffer.getvalue(), content_type="image/png"
        )
        payload = {"image": image}

        res = self.client.post(
            detail_upload_image_recipe_url(recipe.pk),
            payload,
            format="multipart",
        )

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        data = res.data  # type: ignore
        recipe.refresh_from_db()
        self.assertIsNotNone(recipe.image)
        self.assertIn(recipe.image.url, data["image"])
        self.assertIn("uploads/recipes/", recipe.image.path)

    def test_upload_image_recipe_with_invalid_data(self):
        recipe = create_recipe(self.user)
        payload = {}

        res = self.client.post(
            detail_upload_image_recipe_url(recipe.pk),
            payload,
            format="multipart",
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("image", res.data)
