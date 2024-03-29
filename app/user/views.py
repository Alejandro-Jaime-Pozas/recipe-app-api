"""
Views for the user API.
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    serializer_class = AuthTokenSerializer  # this overrides the default username:password auth with our customized AuthTokenSerializer class which is email:password
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES  # this to view in browsable api interface (Swagger)


# RetrieveUpdateAPIView supports GET, PUT and PATCH
class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    serializer_class = UserSerializer
    authentication_classes = [authentication.TokenAuthentication]  # using token auth
    permission_classes = [permissions.IsAuthenticated]  # checking if user has auth permissions

    # override the get_object method from RetrieveUpdateAPIView
    def get_object(self):
        """Retrieve and return the authenticated user."""
        return self.request.user  # request seems to be an already assigned variable for get_object