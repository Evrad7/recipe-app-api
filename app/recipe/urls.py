from rest_framework.routers import DefaultRouter

from recipe.views import RecipeViewSet, TagViewSet

app_name = "recipe"

router = DefaultRouter()

router.register("recipes", RecipeViewSet, basename="recipe")
router.register("tag", TagViewSet, basename="tag")

urlpatterns = router.urls
