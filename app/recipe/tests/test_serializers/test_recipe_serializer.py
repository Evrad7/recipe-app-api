from decimal import Decimal
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from core.models import Recipe
from recipe.serializers import RecipeSerializer


class RecipeSerializerTestCase(APITestCase):

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
            "link": "https://example.com",
        }

        self.recipe = Recipe.objects.create(
            user=self.user,
            title="Pizza Rosto",
            description="Long description of Pizza Rosto",
            duration_minute=9,
            price=Decimal("7.20"),
            link="https://example.com",
        )

    # ========== Tests de sérialisation (lecture) ==========

    def test_serializer_contains_expected_fields(self):
        """Test que la sérialisation contient les bons champs"""
        serializer = RecipeSerializer(self.recipe)
        data = serializer.data

        expected_fields = {"id", "title", "duration_minute", "price", "link"}
        self.assertEqual(expected_fields, set(data.keys()))

        self.assertNotIn("user", data)

    def test_serializer_field_values(self):
        """Test que les valeurs sérialisées sont correctes"""
        serializer = RecipeSerializer(self.recipe)
        data = serializer.data

        self.assertEqual(data["id"], self.recipe.pk)
        self.assertEqual(data["title"], self.recipe.title)
        self.assertEqual(data["duration_minute"], self.recipe.duration_minute)
        self.assertEqual(data["price"], str(self.recipe.price))

    # ========== Tests de validation : title ==========

    def test_title_field_required(self):
        """Test que title est obligatoire"""
        data = self.valid_data.copy()
        del data["title"]

        serializer = RecipeSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_title_cannot_be_empty(self):
        """Test que title ne peut pas être vide"""
        data = self.valid_data.copy()
        data["title"] = ""

        serializer = RecipeSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    def test_title_max_length(self):
        """Test la longueur maximale du titre (255 caractères)"""
        data = self.valid_data.copy()
        data["title"] = "a" * 256

        serializer = RecipeSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("title", serializer.errors)

    # ========== Tests de validation : duration_minute ==========

    def test_duration_minute_field_required(self):
        """Test que duration_minute est obligatoire"""
        data = self.valid_data.copy()
        del data["duration_minute"]

        serializer = RecipeSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("duration_minute", serializer.errors)

    def test_duration_minute_invalid_values(self):
        """Test que duration_minute rejette les valeurs invalides"""
        invalid_values = [-5, 0, 40000]

        for value in invalid_values:
            with self.subTest(duration_minute=value):
                data = self.valid_data.copy()
                data["duration_minute"] = value

                serializer = RecipeSerializer(data=data)

                self.assertFalse(serializer.is_valid())
                self.assertIn("duration_minute", serializer.errors)

    def test_duration_minute_valid_values(self):
        """Test que des valeurs valides sont acceptées"""
        valid_values = [1, 30, 120, 500]

        for value in valid_values:
            with self.subTest(duration_minute=value):
                data = self.valid_data.copy()
                data["duration_minute"] = value

                serializer = RecipeSerializer(data=data)

                self.assertTrue(serializer.is_valid(), serializer.errors)

    # ========== Tests de validation : price ==========

    def test_price_field_required(self):
        """Test que price est obligatoire"""
        data = self.valid_data.copy()
        del data["price"]

        serializer = RecipeSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_price_cannot_be_negative(self):
        """Test que price ne peut pas être négatif"""
        data = self.valid_data.copy()
        data["price"] = "-8.20"

        serializer = RecipeSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_price_invalid_format(self):
        """Test que les formats invalides sont rejetés"""
        invalid_prices = ["abc", "12.345", ""]  # 3 décimales, lettres, vide

        for price in invalid_prices:
            with self.subTest(price=price):
                data = self.valid_data.copy()
                data["price"] = price

                serializer = RecipeSerializer(data=data)

                self.assertFalse(serializer.is_valid())
                self.assertIn("price", serializer.errors)

    # # ========== Tests de validation : link ==========

    # def test_link_not_required(self):
    #     """"Test que les lien n'est pas obligatoire"""
    #     data = self.valid_data.copy()
    #     del data["link"]

    #     serializer = RecipeSerializer(data=data)

    #     self.assertTrue(serializer.is_valid())
    #     self.assertNotIn("link", serializer.data)

    # def test_link_invalid_format(self):
    #     """ Test que les formats invalides de lien sont rejetés"""
    #     invalid_links = ["", "example.com", "test://example.com"]

    #     for link in invalid_links:
    #         with self.subTest(link = link):
    #             data = self.valid_data.copy()
    #             data["link"] = link

    #             serializer = RecipeSerializer(data = data)

    #             self.assertFalse(serializer.is_valid())
    #             self.assertIn("link", serializer.errors)

    # def test_link_valid_format(self):
    #     """ Test que les formats valides ne sont pas rejettés"""

    #     valid_links = ["http://example.com", "https://example.com"]

    #     for link in valid_links:
    #         with self.subTest(link = link):
    #             data = self.valid_data.copy()
    #             data["link"] = link

    #             serializer = RecipeSerializer(data = data)

    #             self.assertTrue(serializer.is_valid())
