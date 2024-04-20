"""
Test for the tags API.
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')


def create_user():
    """Create and return a new user."""
    return get_user_model().objects.create_user(
        email='user@example.com', password='password123'
    )


class PublicTagsAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagsAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)  # force authenticate to be able to make token/auth requests

    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Dessert')

        res = self.client.get(TAGS_URL)

        tags = Tag.objects.all().order_by('-name')  # this to return uniform ordered result in case of diff db
        serializer = TagSerializer(tags, many=True)  # serialize the result of query, and will me multiple obj

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        tag = Tag.objects.create(user=self.user, name='Comfort Food')  # tag created by auth user
        Tag.objects.create(user=user2, name='Fruity')  # tag created by non-auth user

        res = self.client.get(TAGS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # only expect the auth user's tag to be included, not the other user's
        self.assertEqual(res.data[0]['name'], tag.name)  # to check 1st result matches auth user's created tag
        self.assertEqual(res.data[0]['id'], tag.id)