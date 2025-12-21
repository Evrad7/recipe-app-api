from django.db.models import QuerySet
from rest_framework import permissions, serializers, status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import (
    ListModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
)
from rest_framework.validators import ValidationError
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

from drf_spectacular.utils import (
    extend_schema,
    extend_schema_view,
    OpenApiParameter,
)
from drf_spectacular.types import OpenApiTypes


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "tags",
                type=OpenApiTypes.STR,
                description="""Comma separated list of tag ids
                to filter recipes (e.g. 1,2,3)""",
            ),
            OpenApiParameter(
                "ingredients",
                type=OpenApiTypes.STR,
                description="""Comma separated list of ingredient"
                ids to filter recipes (e.g. 5,6)""",
            ),
        ]
    )
)
class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = DetailRecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _convert_params_to_int(self, params: str):
        try:
            return [int(item) for item in params.split(",")]
        except ValueError:
            raise ValidationError("invalid query param format", code="invalid")

    def get_queryset(self):  # type: ignore
        tag_params = self.request.query_params.get("tags", None)
        ingredient_params = self.request.query_params.get("ingredients", None)
        queryset: QuerySet[Recipe] = super().get_queryset()

        if tag_params:
            tag_ids = self._convert_params_to_int(tag_params)
            queryset = queryset.filter(tags__id__in=tag_ids)

        if ingredient_params:
            ingredient_ids = self._convert_params_to_int(ingredient_params)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        queryset = queryset.filter(user=self.request.user).distinct()

        return queryset

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


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "assigned-only",
                type=OpenApiTypes.INT,
                enum=[0, 1],
                description=(
                    "Filter items by assignment to recipes. "
                    "Use `1` to return only items that are assigned \
                        to at least one recipe. "
                    "Use `0` to return all items (default)."
                ),
            )
        ]
    )
)
class BaseRecipeAttrViewSet(
    UpdateModelMixin, ListModelMixin, DestroyModelMixin, GenericViewSet
):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):  # type: ignore
        queryset = super().get_queryset()
        assigned_only = bool(
            int(self.request.query_params.get("assigned-only", 0))
        )
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False).distinct()
        queryset = queryset.filter(user=self.request.user)
        return queryset


class TagViewSet(BaseRecipeAttrViewSet):
    serializer_class = TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()
