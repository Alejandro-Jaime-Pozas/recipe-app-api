"""
Tests for the ingredients API.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


def detail_url(ingredient_id):
    """Create and return an ingredient detail url."""
    return reverse('recipe:ingredient-detail', args=[ingredient_id])  # find the django app named 'recipe', its 'ingredient-detail' auto-generated view, with endpoint of ingredient_id and return the complete url for a single ingredient

def create_user(email='user@example.com', password='password123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIngredientsAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving ingredients."""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        """Test retrieving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Vanilla')

        res = self.client.get(INGREDIENTS_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)  # serialize all of the Ingredient instances already in the Ingredient model
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test list of ingredients is limited to the authenticated user."""
        user2 = create_user(email='user2@example.com')
        Ingredient.objects.create(user=user2, name='Salt')
        ingredient = Ingredient.objects.create(user=self.user, name='Pepper')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # only expecting the ingredient linked to the user
        self.assertEqual(res.data[0]['name'], ingredient.name)  # checking name is auth user created ingredient name
        self.assertEqual(res.data[0]['id'], ingredient.id)  # checking ingredient id from res = auth user ingredient id

    def test_update_ingredient(self):
        """Test updating an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Cilantro')

        payload = {'name': 'Coriander'}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()  # need to refresh since it's already been stored in variable above, the created version, not the updated version
        self.assertEqual(ingredient.name, payload['name'])

    def test_delete_ingredient(self):
        """Test deleting an ingredient."""
        ingredient = Ingredient.objects.create(user=self.user, name='Lettuce')

        url = detail_url(ingredient.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test listing ingredients by those assigned to recipes."""
        ing1 = Ingredient.objects.create(user=self.user, name='Apples')
        ing2 = Ingredient.objects.create(user=self.user, name='Turkey')
        recipe = Recipe.objects.create(
            title='Apple Cruble',
            time_minutes=5,
            price=Decimal('4.50'),
            user=self.user,
        )
        recipe.ingredients.add(ing1)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})  # assigned_only is a parameter value

        s1 = IngredientSerializer(ing1)
        s2 = IngredientSerializer(ing2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)

    def test_filtered_ingredients_unique(self):
        """Test filtered ingredients returns a unique list."""
        ing = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')  # no need to save this ingredient since not assigning
        recipe1 = Recipe.objects.create(
            title='Eggs Benedict',
            time_minutes=50,
            price=Decimal('6.00'),
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='Dragon Eggs',
            time_minutes=20,
            price=Decimal('62.00'),
            user=self.user
        )
        # add ingredient to both recipes
        recipe1.ingredients.add(ing)
        recipe2.ingredients.add(ing)

        res = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)  # data is a list so you can get its length. each item in list should be a different ingredient