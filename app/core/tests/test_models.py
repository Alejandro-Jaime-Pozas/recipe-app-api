"""
Tests for models. Unlike api tests, no requests needed here, just internal.
"""
from unittest.mock import patch  # tool used to mock functions for purposes of testing
from decimal import Decimal

from django.test import TestCase
from django.contrib.auth import get_user_model  # is a helper fn to get the default user model for this project, so if you customize the user model will update here

from core import models  # this to test all of our other built models


def create_user():
    """Create and return a new user."""
    return get_user_model().objects.create_user(
        email='user@example.com',
        password='password123'
    )

# DJANGO TESTS WILL AUTO APPLY ALL MIGRATIONS EVERY TIME YOU DO A TEST RUN AND THEN CLEAR THE MIGRATIONS
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

    # checking that any new email created for a user is capitalized correctly
    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],  # email upper case is typically accepted by providers ONLY before '@' symbol
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')  #input sample email and any pwd (pwd doesnt matter for this test)
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test that creating a user without an email raises a ValueError."""
        #
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'sample123')

    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123',
        )

        self.assertTrue(user.is_superuser)  # django built-in to check if superuser
        self.assertTrue(user.is_staff)  # django built-in to check if staff

    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        # Create a user first
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123',
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title='Sample recipe name',
            time_minutes=5,
            price=Decimal('5.50'),  # best practice for financial data is int type, using Decimal here for simplicity
            description='Sample recipe description.',
        )

        self.assertEqual(str(recipe), recipe.title)  # checking __str__ method for Recipe class is same as recipe instance title

    def test_create_tag(self):
        """Test creating a tag is successful."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test creating an ingredient is successful."""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='Ingredient1',
        )

        self.assertEqual(str(ingredient), ingredient.name)

    # create a test to return a unique url path for a user uploaded media file
    # we're using the patch decorator to modify the uuid functionality to mock its behavior of creating a uuid
    @patch('core.models.uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = 'test-uuid'  # our mocked response for the test
        mock_uuid.return_value = uuid  # setting the mock_uuid's return value (which not sure if builtin) to uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')  # path to image which will be uploaded

        self.assertEqual(file_path, f'uploads/recipe/{uuid}.jpg')