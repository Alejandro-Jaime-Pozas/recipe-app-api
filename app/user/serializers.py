"""
Serializers for the API View.
"""
from django.contrib.auth import (
    get_user_model,
    authenticate  # builtin that allows you to authenticate with django
)
from django.utils.translation import gettext as _

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


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},  # when viewing this in browser, indicates pwd should be hidden
        trim_whitespace=False,  # remove the default of trimming whitespace
    )

    # is called after the data is posted to the view, once we specify the AuthTokenSerializer in the view
    def validate(self, attrs):
        """Validate and authenticate the user."""
        # retrieve email and pwd that the user provided in the post request
        email = attrs.get('email')
        password = attrs.get('password')
        # use authenticate method which requires the request as well as the credentials
        user = authenticate(
            request=self.context.get('request'),  # check why this field is required
            username=email,  # we're using the email as the username..
            password=password,
        )
        # tell the user that we're unable to authenticate with their credentials if no user is returned above
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')

        # set the user attribute to the returned validated/authenticated user above to use it in the view
        attrs['user'] = user
        return attrs
