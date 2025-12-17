from rest_framework.routers import DefaultRouter

from recipe.views import RecipeViewSet

app_name = "recipe"

router = DefaultRouter()

router.register("recipes", RecipeViewSet, basename="recipe")

urlpatterns = router.urls
