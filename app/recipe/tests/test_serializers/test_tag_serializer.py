from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from core.models import Tag
from recipe.serializers import TagSerializer


class TagSerialiserTestCase(APITestCase):

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            **{"email": "test@gmail.com", "password": "123xZPassword"}
        )

        self.tag = Tag.objects.create(user=self.user, name="Meet")

    def test_serializer_contains_expected_fields(self):
        """Test que les serializer contient les valeurs attendues"""
        serializer = TagSerializer(self.tag)

        self.assertEqual({"id", "name"}, set(serializer.data.keys()))
        self.assertNotIn("user", serializer.data)

    # ========== Tests de validation : id ==========

    def test_id_field_cannot_be_written(self):
        """Test que le id ne peux pas être parsé"""
        data = {"id": 7, "name": "Fruity"}

        serializer = TagSerializer(data=data)

        self.assertTrue(serializer.is_valid())
        self.assertNotIn("id", serializer.validated_data)  # type: ignore

    # ========== Tests de validation : name ==========

    def test_name_field_required(self):
        """Test que name est obligatoire"""
        data = {}

        serializer = TagSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_name_field_max_length(self):
        """Test que le name ne dépasse pas la largeur maximale"""
        data = {"name": "a" * 129}

        serializer = TagSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)

    def test_name_field_empty_value(self):
        data = {"name": ""}

        serializer = TagSerializer(data=data)

        self.assertFalse(serializer.is_valid())
        self.assertIn("name", serializer.errors)
