from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from core.models import Ingredient
from recipe.serializers import IngredientSerializer


class IngredientSerializerTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            **{"email": "test@example.com", "password": "123xZPassword"}
        )
        self.ingredient = Ingredient.objects.create(
            user=self.user, name="Vanilla"
        )

    def test_serializer_contains_expected_fields(self):
        """Test serializer for ingredient object return expected fields."""
        serializer = IngredientSerializer(self.ingredient)

        expected_fields = {"id", "name"}
        self.assertSetEqual(expected_fields, set(serializer.data.keys()))
        self.assertNotIn("user", serializer.data)

    # ========== Tests de validation : duration_minute ==========

    def test_name_field_is_required(self):
        """Test that name field is required"""
        data = {}

        serializer = IngredientSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_name_field_is_not_empty(self):
        """Test that name field don't allow empty values"""
        empty_values = ["", None]

        for value in empty_values:
            with self.subTest(invalid_value=value):
                data = {"name": value}

                serializer = IngredientSerializer(data=data)

                self.assertFalse(serializer.is_valid())
                self.assertIn("name", serializer.errors)

    def test_name_field_max_length(self):
        """Test that name field don't exceed max length"""
        data = {"name": "a" * 256}

        serializer = IngredientSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)
