"""
Views for the recipe APIs.
"""
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe
from . import serializers


# this viewset will handle multiple endpoints (list, detail) as well as different actions (GET, POST, PUT, PATCH, DELETE)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeSerializer  # related serializer model to respond to request
    queryset = Recipe.objects.all()  # queryset represents the objects available for this viewset
    authentication_classes = [TokenAuthentication]  # users must have a token
    permission_classes = [IsAuthenticated]  # users must be authenticated

    # overriding the get_queryset fn since need to create specific queryset for user accessing it (otherwise would return result of all global recipes)
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')  # self.request trails back to parent View class's request object. request contains headers, query params, data (request body), and user if auth is required