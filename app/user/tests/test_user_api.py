"""
Tests for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model  # the user model default is changed in 'core' app
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status  # this to access the different http status types ie 200, 400


# this references the api url endpoint that will be used to create users in user app
CREATE_USER_URL = reverse('user:create')  # reverse() takes app name first, then endpoint
TOKEN_URL = reverse('user:token')  # endpoint for creating tokens
ME_URL = reverse('user:me')


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    # setUp is kind of like __init__ method for TestCase class, always runs first
    # since these tests will be for public api use, no authentication is setup
    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating a user is successful."""
        # sample data required to create a user
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        # post the sample data to url endpoint to test creating user
        res = self.client.post(CREATE_USER_URL, payload)  # url is path, payload is data

        # confirm 201 http response
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        # confirm user exists and payload user pwd equals hashed pwd stored in user model
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)  # asserts there is no key named password in http response's data

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email already exists."""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name',
        }
        create_user(**payload)  # pass in unpacked payload to create_user
        res = self.client.post(CREATE_USER_URL, payload)  # try creating user via post method to test if error
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # user exists

    def test_password_too_short_error(self):
        """Test an error is returned if password is less than 8 chars."""
        payload = {
            'email': 'test@example.com',
            'password': '1234567',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)  # should return 400
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()  # returns bool to check the user doesn't exist since pwd is invalid
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        user_details = {
            'email': 'test@example.com',
            'password': 'test-user-password123',
            'name': 'Test Name',
        }
        # create a new user
        create_user(**user_details)

        # add payload to post
        payload = {
            'email': user_details['email'],
            'password': user_details['password'],
        }
        # post the payload to the token url api endpoint
        res = self.client.post(TOKEN_URL, payload)

        # check that a 'token' key is returned in http response data
        self.assertIn('token', res.data)
        # check that status code is 200 success
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Test returns error if credentials invalid."""
        create_user(email='test@example.com', password='goodpass123')

        payload = {
            'email': 'test@example.com',
            'password': 'badpass123',
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_pwd(self):
        """Test posting a blank password returns an error."""
        payload = {'email': 'test@example.com', 'password': ''}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_user_unauthorized(self):
        """Test authentication is required for users."""
        res = self.client.get(ME_URL)  # since this is PublicUserApiTests, should throw auth error

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """Test API requests that require authentication."""

    # since these tests are for private/authenticated test cases, will provide authentication in setUp function
    # remember, the setUp fn always runs first, like the __init__ fn
    def setUp(self):
        self.user = create_user(
            email='test@example.com',
            password='testpass123',
            name='Test Name',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user, )  # forcing authentication to the test user; probably force_authenticate eliminates the need for a token maybe?

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user."""
        res = self.client.get(ME_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': self.user.name,
            'email': self.user.email,
        })

    def test_post_me_not_allowed(self):
        """Test POST is not allowed for the /me/ endpoint."""
        res = self.client.post(ME_URL, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)  # 405 for method not allowed error

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        payload = {'name': 'Updated Name', 'password': 'newpass1234'}

        res = self.client.patch(ME_URL, payload)  # patch as opposed to put updates values in payload, not all of the values from the model/serializer

        self.user.refresh_from_db()  # need to refresh user values from db to get patched updates
        self.assertEqual(self.user.name, payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
