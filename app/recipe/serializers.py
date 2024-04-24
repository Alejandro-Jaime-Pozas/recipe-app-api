"""
Serializers for recipe APIs.
"""
from rest_framework import serializers

from core.models import Recipe, Tag, Ingredient


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name']
        read_only_fields = ['id']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']  # api user should not be able to modify tag id, only other fields


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerializer(many=True, required=False)  # set up a field to TagSerializer with multiple available, but no tags are required (field can be blank)
    ingredients = IngredientSerializer(many=True, required=False)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'title',
            'time_minutes',
            'price',
            'link',
            'tags',  # also add tags field set up above to fields here
            'ingredients',  # also add ingredients field set up above to fields here
        ]
        read_only_fields = ['id']  # api user should not be able to modify recipe id, only other fields


    # using '_' at fn start signifies internal use
    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed."""
        auth_user = self.context['request'].user  # context is a serializer variable passed in from its view
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(  # get or create gets or creates an object
                user=auth_user,  # include the user that is trying to access their Tags
                **tag,  # input all of the tag kwargs required (may update tag reqs which is why **tag helps)
            )
            recipe.tags.add(tag_obj)

    def _get_or_create_ingredients(self, ingredients, recipe):
        """Handle getting or creating ingredients as needed."""
        auth_user = self.context['request'].user  # context is a serializer variable passed in from its view
        for ingredient in ingredients:
            ingredient_obj, created = Ingredient.objects.get_or_create(  # get or create gets or creates an object
                user=auth_user,  # include the user that is trying to access their ingredients
                **ingredient,  # input all of the tag kwargs required (may update tag reqs which is why **tag helps)
            )
            recipe.ingredients.add(ingredient_obj)

    # override the create() fn for ModelSerializer in order to create recipe serializer as well as its tags serializers separately
    def create(self, validated_data):
        """Create a recipe."""
        tags = validated_data.pop('tags', [])  # remove the 'tags' field from validated_data dict and store it, default to [] if no data
        ingredients = validated_data.pop('ingredients', [])
        recipe = Recipe.objects.create(**validated_data)  # create the recipe with updated validated_data (no tags in data)
        self._get_or_create_tags(tags, recipe)
        self._get_or_create_ingredients(ingredients, recipe)

        return recipe

    # override update method for serializers, includes the instance variable which is the existing instance to update
    def update(self, instance, validated_data):  # instance is a RecipeSerializer object
        """Update recipe."""
        tags = validated_data.pop('tags', None)
        # if tags contains tags, clear all of them, then get or create tags from http req
        ingredients = validated_data.pop('ingredients', None)
        if tags is not None:  # if tags is an empty list (as when it's created or tags are removed) this will run
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        if ingredients is not None:
            instance.ingredients.clear()
            self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)  # for each validated key pair, set all instance keys to the new value

        instance.save()
        return instance


# inherit from the RecipeSerializer defined above to extend it
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):  # this inherits from parent's Meta to access all of those configs
        fields = RecipeSerializer.Meta.fields + ['description']  # add this new field to existing fields list