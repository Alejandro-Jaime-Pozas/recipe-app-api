"""
Tests for models.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model  # is a helper fn to get the default user model for this project, so if you customize the user model will update here


# define a test that checks that we can create a user with email and password input successfully
class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with email successful."""
        email = 'test.example.com'  # domain 'example.com' is a reserved domain name for email testing, so no issues when sending emails
        password = 'testpass123'
        # call the custom User model's objects' create_user method
        # get_user_model gets the model; objects is a ref to the User Manager that we'll create;
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))  # like flask, check hashed pwd