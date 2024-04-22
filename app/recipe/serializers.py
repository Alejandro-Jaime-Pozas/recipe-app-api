"""
Serializers for recipe APIs.
"""
from rest_framework import serializers

from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']  # api user should not be able to modify tag id, only other fields


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""
    tags = TagSerializer(many=True, required=False)  # set up a field to TagSerializer with multiple available, but no tags are required (field can be blank)

    class Meta:
        model = Recipe
        fields = [
            'id',
            'title',
            'time_minutes',
            'price',
            'link',
            'tags',  # also add tags field set up above to fields here
        ]
        read_only_fields = ['id']  # api user should not be able to modify recipe id, only other fields

    # override the create() fn for ModelSerializer in order to create recipe serializer as well as its tags serializers separately
    def create(self, validated_data):
        """Create a recipe."""
        tags = validated_data.pop('tags', [])  # remove the 'tags' field from validated_data and store it, default to [] if no data
        recipe = Recipe.objects.create(**validated_data)  # create the recipe with updated validated_data (no tags in data)
        auth_user = self.context['request'].user  # context is a serializer variable passed in from its view
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(  # get or create gets or creates an object
                user=auth_user,  # include the user that is trying to access their Tags
                **tag,  # input all of the tag kwargs required (may update tag reqs which is why **tag helps)
            )
            recipe.tags.add(tag_obj)

        return recipe


# inherit from the RecipeSerializer defined above to extend it
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for recipe detail view."""

    class Meta(RecipeSerializer.Meta):  # this inherits from parent's Meta to access all of those configs
        fields = RecipeSerializer.Meta.fields + ['description']  # add this new field to existing fields list