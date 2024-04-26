"""
Views for the recipe APIs.
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework import viewsets, mixins, status  # mixins are fns you can mix into the view for addtl use
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag, Ingredient
from . import serializers


# ADDED THIS MANUALLY, MAKE SURE PERMISSIONS AND AUTH WORKS ACROSS ALL API ENDPOINTS IN SWAGGER API SITE
class BaseAuthPermissions():
    authentication_classes = [TokenAuthentication]  # users must have a token
    permission_classes = [IsAuthenticated]  # users must be authenticated


# update the api docs auto generated in swagger/drf spectacular schema
@extend_schema_view(
    list=extend_schema(  # 'list' means extend the schema for the list endpoint
        parameters=[  # to define optional parameters than can be passed in for this list API view
            OpenApiParameter(  # to specify the details of a parameter that can be accepted in API requests
                'tags',
                OpenApiTypes.STR,  # str type, since this will be a comma separated str of IDs
                description='Comma separated list of tag IDs to filter',  # displayed for API users
            ),
            OpenApiParameter(
                'ingredients',
                OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter'
            )
        ]
    )
)
# this viewset will handle multiple endpoints (list, detail) as well as different actions (GET, POST, PUT, PATCH, DELETE)
class RecipeViewSet(
    BaseAuthPermissions,
    viewsets.ModelViewSet
):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeDetailSerializer  # related serializer model to respond with to request
    queryset = Recipe.objects.all()  # queryset represents the objects available for this viewset
    # authentication_classes = [TokenAuthentication]  # users must have a token
    # permission_classes = [IsAuthenticated]  # users must be authenticated

    def _params_to_ints(self, qs):
        """Convert a list of strings to integers."""
        return [int(str_id) for str_id in qs.split(',')]  # string in qs looks like this: "1,2,3"

    # overriding the get_queryset fn since need to create specific queryset for user accessing it (otherwise would return result of all global recipes)
    def get_queryset(self):
        """Retrieve recipes for the authenticated user."""
        tags = self.request.query_params.get('tags')  # query_params seems to be like request.user which is included in django view request objects
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset
        if tags:
            # return the queryset of recipes filtered/containing the tags
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredients_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredients_ids)
        return queryset.filter(
            user=self.request.user
        ).order_by('-id').distinct() # self.request trails back to parent View class's request object. request contains headers, query params, data (request body), and user if auth is required

    # manage the serializer returned based on the request
    def get_serializer_class(self):
        """Return the serializer class for request."""
        # if the action is a list action (not detail) then return a list, else detail
        if self.action == 'list':
            return serializers.RecipeSerializer  # return reference to class, not an instance
        elif self.action == 'upload_image':  # upload_image is a custom action we define in our recipe viewset
            return serializers.RecipeImageSerializer
        return self.serializer_class

    # use builtin perform_create to modify how django saves a serializer/model (should only apply to POST method)
    def perform_create(self, serializer):  # serializer is already validated prior to this fn call
        """Create a new recipe."""
        serializer.save(user=self.request.user)  # this to save the active user as the specified recipe user FK

    # adding a custom action with action decorator to handle user image upload
    @action(methods=['POST'], detail=True, url_path='upload-image')  # POST only for image creation; detail True means for a specific image, not list; url path is a custom url path where our action takes place
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe."""
        recipe = self.get_object()  # gets the object based on serializer class/queryset using its id
        serializer = self.get_serializer(recipe, data=request.data)  # will trigger fn get_serializer_class and return recipe image serializer as specified there

        # returning responses here like flask routes files if requests are valid/invalid
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseRecipeAttrViewSet(
    BaseAuthPermissions,
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