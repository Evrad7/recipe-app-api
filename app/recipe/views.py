from rest_framework import permissions, serializers
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import (
    ListModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)

from core.models import Ingredient, Recipe, Tag
from recipe.serializers import (
    DetailRecipeSerializer,
    IngredientSerializer,
    RecipeSerializer,
    TagSerializer,
)


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = DetailRecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):  # type: ignore
        return Recipe.objects.filter(user=self.request.user)

    def perform_create(self, serializer: serializers.BaseSerializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):  # type: ignore
        if self.action == "list":
            return RecipeSerializer
        return self.serializer_class


class TagViewSet(
    UpdateModelMixin, ListModelMixin, DestroyModelMixin, GenericViewSet
):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):  # type: ignore
        return Tag.objects.filter(user=self.request.user)


class IngredientViewSet(
    UpdateModelMixin, ListModelMixin, DestroyModelMixin, GenericViewSet
):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):  # type: ignore
        return Ingredient.objects.filter(user=self.request.user)
