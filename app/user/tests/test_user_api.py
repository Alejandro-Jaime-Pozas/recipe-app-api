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


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    # setUp is kind of like __init__ method for TestCase class, always runs first
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