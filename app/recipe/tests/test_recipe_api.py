"""
Tests for recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import (
RecipeSerializer,
RecipeDetailSerializer,
)


RECIPES_URL = reverse('recipe:recipe-list')  # gets the url endpoint

# defining detail_url as function vs constant (as RECIPES_URL) since the detail requires a unique id
def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])  # pass in the name of the view, and recipe id as arg

# Helper function that we will use often to test the CRUD capabilites of recipe API (no 'test' in fn name)
def create_recipe(user, **params):
    """Create and return a sample recipe."""
    # assign default values that will be used to create a recipe for tests
    defaults = {
        'title': 'Sample recipe title.',
        'description': 'Sample description',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'link': 'http://example.com/recipe.pdf',
    }
    defaults.update(params)  # add params dict or kwargs to defaults dict; order matters, params will override defaults if same key name in this case

    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe


class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    # recipes will only be available in private API cases, not public, so test for that
    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'testpass123',
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        # accessing global scoped create_recipe fn at top
        create_recipe(user=self.user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)  # since we're creating 2 recipes above with same default user, should return both recipes (not globally all recipes in backend regardless of user)

        recipes = Recipe.objects.all().order_by('-pk')  # order recipes by pk/id descending (most recent)
        serializer = RecipeSerializer(recipes, many=True)  # serializers can return one item (detail) or a list of items; many is builtin attr to indicate multiple objects

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)  # make sure the data dict returned in the http response is equal to serializer.data (which is not clear how that works)

    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = get_user_model().objects.create_user(
            'other@example.com',
            'passowrd123',
        )
        create_recipe(user=other_user)
        create_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)  # since we're creating 2 recipes above with diff users, should return only 1 recipe for user in setUp fn (not globally all recipes in backend regardless of user)

        recipes = Recipe.objects.filter(user=self.user)  # filtering only recipes for authenticated user
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe(user=self.user)  # create recipe with default test user from setUp fn

        url = detail_url(recipe.id)  # create a detail url using detail_url defined above
        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)  # don't pass in Many=True since just one instance

        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            'title': 'Sample recipe',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(RECIPES_URL, payload)  # post the sample payload to recipes url

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)  # check status code is 201 created
        recipe = Recipe.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)  # getattr() needed for class objects (ie __Recipe__ class isntance)
        self.assertEqual(recipe.user, self.user)