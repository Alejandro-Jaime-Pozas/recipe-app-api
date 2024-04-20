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


TAGS_URL = reverse('recipe:tag-list')  # url for tag list (to get all tags); first part is app_name in urls.py, second part is auto-generated django url endpoint in urls.py


def detail_url(tag_id):
    """Create and return a tag detail url."""
    return reverse('recipe:tag-detail', args=[tag_id])


def create_user(email='user@example.com', password='password123'):
    """Create and return a new user."""
    return get_user_model().objects.create_user(email=email, password=password)


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

    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, name='After Dinner')

        payload = {'name': 'Dessert'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        tag.refresh_from_db()  # required for put/patch
        self.assertEqual(tag.name, payload.get('name'))

    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(user=self.user, name='Breakfast')

        url = detail_url(tag.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())  # user should have no tags