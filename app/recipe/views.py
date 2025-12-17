from rest_framework import permissions, serializers
from rest_framework.viewsets import ModelViewSet

from core.models import Recipe
from recipe.serializers import DetailRecipeSerializer, RecipeSerializer


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
