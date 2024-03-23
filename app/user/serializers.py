"""
Serializers for the API View.
"""
from django.contrib.auth import get_user_model

from rest_framework import serializers  # serializers validates data before inputting into a model


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""

    class Meta:
        # set model to User
        model = get_user_model()  # for some reason here you call fn() vs referencing it
        fields = ['email', 'password', 'name', ]  # fields already included in User model; excluding is_staff and admin related fields here for security
        extra_kwargs = {
            'password': {
                'write_only': True,  # make sure pwd is not read after creation
                'min_length': 8,
            }
        }  # extra_kwargs provides additional settings for fields;

    # create method allows us to overwrite the default ModelSerializer create method; this create method will only be called (automatically) if the serializer validation is succesful, meaning all inputs are validated based on restrictions/configuration
    def create(self, validated_data):
        """Create and return a user with encrypted password."""
        # we want to overwrite the default builtin create method and create user based on our own User model
        return get_user_model().objects.create_user(**validated_data)