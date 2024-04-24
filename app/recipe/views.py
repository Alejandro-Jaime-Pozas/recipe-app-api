"""
Views for the recipe APIs.
"""
from rest_framework import viewsets, mixins  # mixins are fns you can mix into the view for addtl use
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from . import serializers


# ADDED THIS MANUALLY, MAKE SURE PERMISSIONS AND AUTH WORKS ACROSS ALL API ENDPOINTS IN SWAGGER API SITE
class BaseAuthPermissionsViewSet():
    authentication_classes = [TokenAuthentication]  # users must have a token
    permission_classes = [IsAuthenticated]  # users must be authenticated


# this viewset will handle multiple endpoints (list, detail) as well as different actions (GET, POST, PUT, PATCH, DELETE)
class RecipeViewSet(
    BaseAuthPermissionsViewSet,
    viewsets.ModelViewSet
):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeDetailSerializer  # related serializer model to respond with to request
    queryset = Recipe.objects.all()  # queryset represents the objects available for this viewset
    # authentication_classes = [TokenAuthentication]  # users must have a token
    # permission_classes = [IsAuthenticated]  # users must be authenticated

    # overriding the get_queryset fn since need to create specific queryset for user accessing it (otherwise would return result of all global recipes)
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')  # self.request trails back to parent View class's request object. request contains headers, query params, data (request body), and user if auth is required

    # manage the serializer returned based on the request
    def get_serializer_class(self):
        """Return the serializer class for request."""
        # if the action is a list action (not detail) then return a list, else detail
        if self.action == 'list':
            return serializers.RecipeSerializer  # return reference to class, not an instance
        return self.serializer_class

    # use builtin perform_create to modify how django saves a serializer/model (should only apply to POST method)
    def perform_create(self, serializer):  # serializer is already validated prior to this fn call
        """Create a new recipe."""
        serializer.save(user=self.request.user)  # this to save the active user as the specified recipe user FK


class BaseRecipeAttrViewSet(
    BaseAuthPermissionsViewSet,
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,  # important to ALWAYS DEFINE MIXINS BEFORE VIEWSETS or they'll be overwritten
    viewsets.GenericViewSet,
):
    """Base viewset for recipe attributes."""

    def get_queryset(self):
        """Filter queryset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')


class TagViewSet(BaseRecipeAttrViewSet):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()


class IngredientViewSet(BaseRecipeAttrViewSet):
    """Manage ingredients in the database."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()