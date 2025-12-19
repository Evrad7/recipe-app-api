from rest_framework import serializers

from core.models import Ingredient, Recipe, Tag


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ["id", "name"]


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ["id", "name"]
        read_only_fields = ["id"]


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            "id",
            "title",
            "duration_minute",
            "price",
            "link",
            "tags",
            "ingredients",
        ]
        read_only_fields = ["id"]
        extra_kwargs = {"link": {"allow_blank": False}}


class DetailRecipeSerializer(RecipeSerializer):

    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ["description"]

    def _get_or_create_tags(self, instance, data):
        tags = []
        user = self.context["request"].user
        for datum in data:
            tag, _ = Tag.objects.get_or_create(user=user, **datum)
            tags.append(tag)
        instance.tags.set(tags)

    def _get_or_create_ingredients(self, instance, data):
        ingredients = []
        user = self.context["request"].user
        for datum in data:
            ingredient, _ = Ingredient.objects.get_or_create(
                user=user, **datum
            )
            ingredients.append(ingredient)
        instance.ingredients.set(ingredients)

    def create(self, validated_data):
        tags_data = validated_data.pop("tags", [])
        ingredients_data = validated_data.pop("ingredients", [])
        recipe = Recipe.objects.create(**validated_data)
        self._get_or_create_tags(recipe, tags_data)
        self._get_or_create_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop("tags", [])
        ingredients_data = validated_data.pop("ingredients", [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        self._get_or_create_tags(instance, tags_data)
        self._get_or_create_ingredients(instance, ingredients_data)
        return instance
