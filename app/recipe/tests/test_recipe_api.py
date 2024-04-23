"""
Tests for recipe APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag

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

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


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
        self.user = create_user(email='user@example.com', password='password123')
        self.client.force_authenticate(self.user)  # forcing authentication to the test user; probably force_authenticate eliminates the need for a token maybe?

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
        other_user = create_user(email='other@example.com', password='password123',)
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

    def test_partial_update(self):
        """Test partial update of a recipe."""
        original_link = 'https://example.com/recipe.pdf'  # this to test partial update doesn't affect recipe link
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link=original_link,
        )
        url = detail_url(recipe.id)  # create a detail url based on the recipe id
        payload = {'title': 'NEW recipe title'}  # change just 1 field in recipe
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()  # by default the db model is not refreshed on patch method, so need to refresh
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)  # to check original link did not change
        self.assertEqual(recipe.user, self.user)

    def test_full_update(self):
        """Test full update of recipe."""
        recipe = create_recipe(
            user=self.user,
            title='Sample recipe title',
            link='https://example.com/recipe.pdf',
            description='Sample recipe description.',
        )

        # include ALL modifiable fields for full update of a user's recipe
        payload = {
            'title': 'NEW recipe title',
            'link':'https://example.com/new-recipe.pdf',
            'description':'NEW recipe description.',
            'time_minutes': 10,
            'price': Decimal('2.50'),
        }
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)

    def test_update_recipe_user_returns_error(self):
        """Test changing the recipe user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        recipe = create_recipe(user=self.user)

        payload = {'user': new_user.pk}
        url = detail_url(recipe.id)
        self.client.patch(url, payload)

        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe successful."""
        recipe = create_recipe(user=self.user)
        url = detail_url(recipe.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)  # should return no content
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())  # check recipe no longer exists in db

    def test_recipe_other_users_recipe_error(self):
        """Test trying to delete another users recipe gives error."""
        new_user = create_user(email='user3@example.com', password='password123')
        recipe = create_recipe(user=new_user)  # should allow new user to create recipe

        url = detail_url(recipe.id)
        res = self.client.delete(url)  # should NOT allow delete since curr active user in setUp is NOT new_user

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())  # check recipe still exists

    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')  # since there's nested objects (tags) need to specify format is json

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)  # get all auth user's recipes
        self.assertEqual(recipes.count(), 1)  # confirm auth user only has 1 recipe
        recipe = recipes[0]  # get the first item from recipes, which is the only recipe created
        self.assertEqual(recipe.tags.count(), 2)  # make sure the 2 tags created within the recipe exist
        # further check that the tags in payload are owned by the auth user and that their names are the same
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tag."""
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('5.00'),
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}],
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)  # should just be 1 recipe
        recipe = recipes[0]  # grab the first recipe from user's recipes
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())  # check that the Tag object named 'Indian' is in recipe's tags
        for tag in payload['tags']:
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)  # check that each of the posted tags exists within the user's created recipe

    def test_create_tag_on_update(self):
        """Test creating tag when updating a recipe."""
        recipe = create_recipe(user=self.user)
        payload = {'tags': [{'name': 'Lunch'}]}  # payload contains list of just one tag
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')  # only update recipe values in the payload

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Lunch')  # get the created tag from the recipe obj
        self.assertIn(new_tag, recipe.tags.all())  # check tag in recipe tags; no need for refresh_from_db() since we're querying recipe.tags.all(), not the new_tag obj

    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe."""
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')  # this patch somehow utilizes either the model or serializes update() builtin method

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())  # check lunch tag replaced breakfast tag
        self.assertNotIn(tag_breakfast, recipe.tags.all())  # check breakfast tag no longer exists with that name

    def test_clear_recipe_tags(self):
        """Test clearing a recipe's tags."""
        tag = Tag.objects.create(user=self.user, name='Desert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)  # add new tag to the new recipe

        payload = {'tags': []}  # pass in empty list for tags
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')  # json format since 'tags' is object and not string..

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)  # make sure there's no objects in the tags field for this recipe