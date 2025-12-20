from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import override_settings
from rest_framework.test import APITestCase

from core.models import Recipe
from recipe.serializers import ImageRecipeSerializer


@override_settings(MEDIA_ROOT="/tmp")
class ImageRecipeSerializerTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            **{"email": "test@example.com", "password": "123xZPassword"}
        )

        self.recipe = Recipe.objects.create(
            user=self.user,
            title="Pasta gold",
            description="Pasta fruit",
            duration_minute=5,
            price=Decimal("19.9"),
        )

    def tearDown(self) -> None:
        self.recipe.image.delete(save=False)

    def test_serializer_contains_expected_fields(self):
        serializer = ImageRecipeSerializer(self.recipe)

        expected_fields = {"id", "image"}
        self.assertSetEqual(expected_fields, set(serializer.data.keys()))

    def test_field_image_is_required(self):
        data = {}
        serializer = ImageRecipeSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("image", serializer.errors)
