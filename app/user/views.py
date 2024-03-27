"""
Views for the user API.
"""
from rest_framework import generics
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