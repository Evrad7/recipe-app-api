from rest_framework import permissions, serializers, status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import (
    ListModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import Ingredient, Recipe, Tag
from recipe.serializers import (
    DetailRecipeSerializer,
    ImageRecipeSerializer,
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
        if self.action == "upload_image":
            return ImageRecipeSerializer
        return self.serializer_class

    @action(
        methods=["POST"],
        detail=True,
        url_name="upload_image",
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


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
