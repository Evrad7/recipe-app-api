from decimal import Decimal
from unittest.mock import MagicMock
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from core.models import Recipe, Tag
from recipe.serializers import DetailRecipeSerializer


class DetailRecipeSerializerTestCase(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@gmail.com",
            password="123xZStrongPassword",
            name="Test",
        )  # type: ignore

        self.valid_data = {
            "title": "Pasta Gold",
            "description": "Long description of pasta gold recipe",
            "duration_minute": 7,
            "price": "5.90",
        }

        self.recipe = Recipe.objects.create(
            user=self.user,
            title="Pizza Rosto",
            description="Long description of Pizza Rosto",
            duration_minute=9,
            price=Decimal("7.20"),
        )

        self.mocked_request = MagicMock()
        self.mocked_request.user = self.user

    # ========== Tests de sérialisation (lecture) ==========

    def test_serializer_contains_expected_fields(self):
        """Test que la sérialisation contient les bons champs"""
        serializer = DetailRecipeSerializer(self.recipe)
        data = serializer.data

        expected_fields = {
            "id",
            "title",
            "description",
            "duration_minute",
            "price",
            "link",
            "tags",
        }
        self.assertEqual(expected_fields, set(data.keys()))

    def test_serializer_field_values(self):
        """Test que les valeurs sérialisées sont correctes"""
        serializer = DetailRecipeSerializer(self.recipe)
        data = serializer.data

        self.assertEqual(data["description"], self.recipe.description)

    # ========== Tests de validation : description ==========

    def test_description_field_required(self):
        """Test que description est obligatoire"""
        data = self.valid_data.copy()
        del data["description"]

        serializer = DetailRecipeSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("description", serializer.errors)

    def test_description_cannot_be_empty(self):
        """Test que description ne peut pas être vide"""
        data = self.valid_data.copy()
        data["description"] = ""

        serializer = DetailRecipeSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("description", serializer.errors)

    def test_create_recipe_with_tag(self):
        """Test that serializer create recipe with tags with sucess"""
        data = {
            "title": "Tortilla",
            "description": "Tortillas dishes, follow intructions ...",
            "price": Decimal("5.8"),
            "duration_minute": 8,
            "tags": [{"name": "Fruit"}, {"name": "Meet"}],
        }
        serializer = DetailRecipeSerializer(
            data=data, context={"request": self.mocked_request}
        )
        self.assertTrue(serializer.is_valid())

        serializer.save(user=self.user)

        recipe = Recipe.objects.filter(user=self.user)[0]
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertEqual(recipe.title, data["title"])
        self.assertEqual(recipe.description, data["description"])
        self.assertEqual(recipe.price, data["price"])
        self.assertEqual(recipe.duration_minute, data["duration_minute"])
        for i, tag in enumerate(tags):
            self.assertEqual(tag.name, data["tags"][i]["name"])

    def test_create_recipe_with_existing_tag(self):
        """Test that serializer create recipe with tag that already
        exists with sucess"""
        tag = Tag.objects.create(user=self.user, name="Fruit")
        data = {
            "title": "Tortilla",
            "description": "Tortillas dishes, follow intructions ...",
            "price": Decimal("5.8"),
            "duration_minute": 8,
            "tags": [{"name": tag.name}, {"name": "Meet"}],
        }
        serializer = DetailRecipeSerializer(
            data=data, context={"request": self.mocked_request}
        )
        self.assertTrue(serializer.is_valid())

        serializer.save(user=self.user)

        recipe = Recipe.objects.filter(user=self.user)[0]
        tags = recipe.tags.order_by("name")
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag, tags)
        for i, tag in enumerate(tags):
            self.assertEqual(tag.name, data["tags"][i]["name"])

    def test_update_recipe_with_tag(self):
        """Test that serializer update recipe with tag successfully."""
        recipe = Recipe.objects.create(
            user=self.user,
            title="Pasta",
            description="Pasta instructions ...",
            price=Decimal("5.9"),
            duration_minute=20,
        )
        data = {
            "title": "Pasta gold updated",
            "tags": [{"name": "France"}, {"name": "India"}],
        }
        serializer = DetailRecipeSerializer(
            recipe,
            data=data,
            partial=True,
            context={"request": self.mocked_request},
        )
        self.assertTrue(serializer.is_valid())

        serializer.save(user=self.user)

        recipe.refresh_from_db()
        tags = recipe.tags.order_by("name")
        self.assertEqual(tags.count(), 2)
        self.assertEqual(recipe.title, data["title"])
        for i, tag in enumerate(tags):
            self.assertEqual(tag.name, data["tags"][i]["name"])

    def test_update_recipe_with_existing_tag(self):
        """Test that serializer update recipe with existing tag successfully"""
        tag = Tag.objects.create(user=self.user, name="Fruity")
        recipe = Recipe.objects.create(
            user=self.user,
            title="Pasta",
            description="Pasta instructions ...",
            price=Decimal("5.9"),
            duration_minute=20,
        )
        recipe.tags.add(tag)
        data = {
            "title": "Totillas",
            "tags": [{"name": tag.name}, {"name": "India"}],
        }
        serializer = DetailRecipeSerializer(
            recipe,
            data=data,
            partial=True,
            context={"request": self.mocked_request},
        )
        self.assertTrue(serializer.is_valid())

        serializer.save(user=self.user)

        tags = recipe.tags.order_by("name")
        recipe.refresh_from_db()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag, tags)
        for i, tag in enumerate(tags):
            self.assertEqual(tag.name, data["tags"][i]["name"])

    def test_update_recipe_with_empty_tags(self):
        """Test clear tags when updating whith empty tags"""
        tag = Tag.objects.create(user=self.user, name="Fruity")
        recipe = Recipe.objects.create(
            user=self.user,
            title="Pasta",
            description="Pasta instructions ...",
            price=Decimal("5.9"),
            duration_minute=20,
        )
        recipe.tags.add(tag)
        data = {"title": "Rosta bouill", "tags": []}
        serializer = DetailRecipeSerializer(
            recipe,
            data=data,
            partial=True,
            context={"request": self.mocked_request},
        )
        self.assertTrue(serializer.is_valid())

        serializer.save(user=self.user)

        self.assertFalse(recipe.tags.exists())
