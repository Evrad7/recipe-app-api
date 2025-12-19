from rest_framework.routers import DefaultRouter

from recipe.views import IngredientViewSet, RecipeViewSet, TagViewSet

app_name = "recipe"

router = DefaultRouter()

router.register("recipes", RecipeViewSet, basename="recipe")
router.register("tags", TagViewSet, basename="tag")
router.register("ingredients", IngredientViewSet, basename="ingredient")

urlpatterns = router.urls
