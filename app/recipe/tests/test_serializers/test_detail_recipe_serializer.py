from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from core.models import Recipe
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
        }
        self.assertEqual(expected_fields, set(data.keys()))

    def test_serializer_field_values(self):
        """Test que les valeurs sérialisées sont correctes"""
        serializer = DetailRecipeSerializer(self.recipe)
        data = serializer.data

        self.assertEqual(data["id"], self.recipe.pk)
        self.assertEqual(data["title"], self.recipe.title)
        self.assertEqual(data["description"], self.recipe.description)
        self.assertEqual(data["duration_minute"], self.recipe.duration_minute)
        self.assertEqual(data["price"], str(self.recipe.price))

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
